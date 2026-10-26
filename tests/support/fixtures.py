from __future__ import annotations

import platform
import re
import shutil
from collections.abc import Iterator
from contextlib import ExitStack
from pathlib import Path
from uuid import uuid4

import allure
import pytest
from playwright.sync_api import Browser, BrowserContext, Page, sync_playwright

from config.settings import settings
from datafactory.login.LoginData import get_valid_login_credentials
from pageobjects.login.LoginPage import LoginPage

RUN_ID = uuid4().hex
ARTIFACT_DIR = Path(settings.artifact_dir) / RUN_ID
ALLURE_BDD_STEP_CONTEXT: pytest.StashKey[ExitStack] = pytest.StashKey()
BDD_SCENARIO_NAME: pytest.StashKey[str] = pytest.StashKey()
SCENARIO_NAMES: dict[str, str] = {}
PENDING_REPORTS: dict[str, list[pytest.TestReport]] = {}


def _take_allure_bdd_step(request: pytest.FixtureRequest) -> ExitStack | None:
    if ALLURE_BDD_STEP_CONTEXT not in request.node.stash:
        return None

    stack = request.node.stash[ALLURE_BDD_STEP_CONTEXT]
    del request.node.stash[ALLURE_BDD_STEP_CONTEXT]
    return stack


def _safe_name(value: str) -> str:
    """Convert a test name into a filesystem-safe name."""
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return name or "test"


def _scenario_dir(item: pytest.Item) -> Path:
    scenario_name = item.stash.get(BDD_SCENARIO_NAME, item.name)
    return ARTIFACT_DIR / _safe_name(scenario_name)


def _scenario_dir_for_name(scenario_name: str) -> Path:
    return ARTIFACT_DIR / _safe_name(scenario_name)


def _write_scenario_report(report: pytest.TestReport, scenario_name: str) -> None:
    scenario_dir = _scenario_dir_for_name(scenario_name)
    scenario_dir.mkdir(parents=True, exist_ok=True)
    log_path = scenario_dir / "scenario.log"

    with log_path.open("a", encoding="utf-8") as log_file:
        log_file.write(f"{report.when.upper()}: {report.outcome}\n")
        for heading, content in report.sections:
            log_file.write(f"\n--- {heading} ---\n{content}\n")
        if report.failed and report.longrepr:
            log_file.write(f"\n--- Failure ---\n{report.longreprtext}\n")
        log_file.write("\n")


def _test_failed(request: pytest.FixtureRequest) -> bool:
    """Check whether test setup or execution failed."""
    reports = (
        getattr(request.node, "rep_setup", None),
        getattr(request.node, "rep_call", None),
    )
    return any(report is not None and report.failed for report in reports)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Make setup, call, and teardown results available to fixtures."""
    outcome = yield
    report = outcome.get_result()
    setattr(item, f"rep_{report.when}", report)


def pytest_sessionstart(session: pytest.Session) -> None:
    """Remove outputs from previous framework runs before starting a fresh run."""
    for output_root in (Path(settings.artifact_dir), Path("logs")):
        if not output_root.exists():
            continue

        for previous_output in output_root.rglob("*"):
            if (
                previous_output.is_file()
                and previous_output.suffix.lower() in {".log", ".png", ".webm", ".zip"}
            ):
                previous_output.unlink()

        for previous_run in output_root.iterdir():
            if previous_run.is_dir() and re.fullmatch(r"[0-9a-f]{32}", previous_run.name):
                shutil.rmtree(previous_run)

    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    """Keep each test's result and failure details beside its browser artifacts."""
    scenario_name = SCENARIO_NAMES.get(report.nodeid)
    if scenario_name is None:
        PENDING_REPORTS.setdefault(report.nodeid, []).append(report)
        return

    _write_scenario_report(report, scenario_name)


def pytest_bdd_before_scenario(request, feature, scenario) -> None:
    """Set Allure scenario metadata from the feature file."""
    request.node.stash[BDD_SCENARIO_NAME] = scenario.name
    SCENARIO_NAMES[request.node.nodeid] = scenario.name
    for report in PENDING_REPORTS.pop(request.node.nodeid, []):
        _write_scenario_report(report, scenario.name)
    tags = feature.tags | scenario.tags
    allure.dynamic.epic("OrangeHRM")
    allure.dynamic.feature(feature.name.replace("OrangeHRM ", "", 1))
    allure.dynamic.story(scenario.name)
    allure.dynamic.title(scenario.name)
    if tags:
        allure.dynamic.tag(*sorted(tags))
    severity = (
        allure.severity_level.CRITICAL
        if "smoke" in tags
        else allure.severity_level.NORMAL
    )
    allure.dynamic.severity(severity)


def pytest_bdd_before_step(
    request,
    feature,
    scenario,
    step,
    step_func,
) -> None:
    """Report each Gherkin step using its feature-file keyword and text."""
    stack = ExitStack()
    stack.enter_context(allure.step(f"{step.keyword.strip()} {step.name}"))
    request.node.stash[ALLURE_BDD_STEP_CONTEXT] = stack


def pytest_bdd_after_step(
    request,
    feature,
    scenario,
    step,
    step_func,
    step_func_args,
) -> None:
    """Close the Allure step after a successful Gherkin step."""
    stack = _take_allure_bdd_step(request)
    if stack is not None:
        stack.close()


def pytest_bdd_step_error(
    request,
    feature,
    scenario,
    step,
    step_func,
    step_func_args,
    exception,
) -> None:
    """Mark the active Allure step failed when a Gherkin step raises."""
    stack = _take_allure_bdd_step(request)
    if stack is not None:
        stack.__exit__(type(exception), exception, exception.__traceback__)


@pytest.fixture(scope="session", autouse=True)
def prepare_run_output_directories() -> None:
    """Create output directories unique to this pytest process."""
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)


@pytest.fixture(scope="function")
def browser_context(
    request: pytest.FixtureRequest,
) -> Iterator[BrowserContext]:
    """Create an isolated browser context for one test."""
    temporary_dir = ARTIFACT_DIR / _safe_name(request.node.name)
    video_dir = temporary_dir / "video"

    with sync_playwright() as playwright:
        browser_type = getattr(playwright, settings.browser_name)
        if settings.browser_name == "chromium":
            browser: Browser = browser_type.launch(
                headless=settings.headless,
                args=["--start-maximized"],
            )
        else:
            browser = browser_type.launch(headless=settings.headless)

        context_options = {
            "no_viewport": True,
        }

        if settings.video_on_failure:
            video_dir.mkdir(parents=True, exist_ok=True)
            context_options["record_video_dir"] = str(video_dir)
            context_options["record_video_size"] = {
                "width": 1920,
                "height": 1080,
            }

        context = browser.new_context(**context_options)
        context.set_default_timeout(settings.timeout)

        if settings.trace_on_failure:
            context.tracing.start(
                screenshots=True,
                snapshots=True,
                sources=True,
            )

        try:
            yield context
        finally:
            failed = _test_failed(request)
            scenario_dir = _scenario_dir(request.node)

            try:
                if settings.trace_on_failure:
                    if failed:
                        scenario_dir.mkdir(parents=True, exist_ok=True)
                        scenario_dir.mkdir(parents=True, exist_ok=True)
                        trace_path = scenario_dir / "trace.zip"
                        context.tracing.stop(path=str(trace_path))
                        allure.attach.file(
                            str(trace_path),
                            name=f"{scenario_dir.name} - Playwright trace",
                            attachment_type=allure.attachment_type.ZIP,
                        )
                    else:
                        context.tracing.stop()
            finally:
                try:
                    context.close()
                finally:
                    browser.close()

            if settings.video_on_failure and video_dir.exists() and not failed:
                shutil.rmtree(video_dir)
                if not any(temporary_dir.iterdir()):
                    temporary_dir.rmdir()
            elif settings.video_on_failure and video_dir.exists():
                final_video_dir = scenario_dir / "video"
                if video_dir != final_video_dir:
                    final_video_dir.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(video_dir), str(final_video_dir))
                    if not any(temporary_dir.iterdir()):
                        temporary_dir.rmdir()


@pytest.fixture(scope="function")
def page(
    browser_context: BrowserContext,
    request: pytest.FixtureRequest,
) -> Iterator[Page]:
    """Create a page and save a screenshot if its test fails."""
    page = browser_context.new_page()

    try:
        yield page
    finally:
        try:
            if _test_failed(request) and settings.screenshot_on_failure:
                scenario_dir = _scenario_dir(request.node)
                scenario_dir.mkdir(parents=True, exist_ok=True)
                screenshot_path = scenario_dir / "screenshot.png"
                screenshot = page.screenshot(path=str(screenshot_path), full_page=True)
                allure.attach(
                    screenshot,
                    name=f"{scenario_dir.name} - failure screenshot",
                    attachment_type=allure.attachment_type.PNG,
                )
        finally:
            page.close()


@pytest.fixture(autouse=True)
def login_before_each_test(
    request: pytest.FixtureRequest,
    page: Page,
) -> None:
    """Start each test with an authenticated OrangeHRM session."""
    if request.node.get_closest_marker("handles_login") is not None:
        return

    login = get_valid_login_credentials(settings)
    login_page = LoginPage(page, settings)
    login_page.navigate_to()
    login_page.enterLoginDataAndClickLogin(login.username, login.password)


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Write non-sensitive run metadata for the Allure environment section."""
    for nodeid, reports in PENDING_REPORTS.items():
        scenario_name = SCENARIO_NAMES.get(nodeid, nodeid)
        for report in reports:
            _write_scenario_report(report, scenario_name)

    allure_results = session.config.getoption("--alluredir")
    if not allure_results:
        return

    results_dir = Path(allure_results)
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / "environment.properties").write_text(
        "\n".join(
            (
                f"Browser={settings.browser_name}",
                f"Application URL={settings.base_url}",
                f"Python={platform.python_version()}",
                f"Platform={platform.system()}",
            )
        ),
        encoding="utf-8",
    )