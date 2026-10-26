# Playwright Python BDD Framework

This repository contains a lightweight enterprise-ready Playwright + pytest-bdd framework for browser automation. It follows a page-object model layered with BDD step definitions and a central browser fixture lifecycle.

## Structure

- `src/config/` — environment-backed framework settings
- `src/datafactory/` and `src/models/` — login test data and its model
- `src/pageobjects/` — shared page behavior and page objects
- `tests/features/` and `tests/steps/` — Gherkin scenario and pytest-bdd steps
- `tests/support/` — browser and page fixtures
- `.vscode/` — test discovery, scenario runner, and browser tasks

## Quick start

1. Create the virtual environment.
2. Install dependencies and the package in editable mode.
3. Install the Playwright browser binaries you plan to use.

PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m playwright install chromium firefox webkit
```

POSIX:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
python -m playwright install chromium firefox webkit
```

## Configuration

The framework resolves settings in this order:

1. Environment variables from the shell
2. Values in the root `.env.prod` file when running pytest (shell values take precedence)
3. Defaults in `src/config/settings.py`

Copy `.env.example` to the ignored `.env.prod` file, then set `APP_USERNAME` and
`APP_PASSWORD` to run the login scenario. Shell environment variables take precedence over
values loaded from `.env.prod`.
`BROWSER` selects `chromium`, `firefox`, or `webkit`; `HEADLESS=false` runs a visible browser.

## Running tests

```bash
pytest
```

Pytest writes Allure result files to `allure-results/` and cleans that directory at the start
of each run. The results include scenario labels, named BDD steps, run environment details, and
failure screenshots, videos, and Playwright traces. Generate and open the HTML report with the
Allure command-line tool:

```bash
allure serve allure-results
```

In VS Code, install the recommended extensions to get a Run button above each Gherkin scenario
and pytest test discovery. The scenario button runs the matching pytest-bdd test. Use the
`Test: Chromium`, `Test: Firefox`, and `Test: WebKit` tasks to run tests in one browser, or
`Test: All Browsers` to run them sequentially in all three.

To run a tagged scenario directly, pass its feature and scenario tags to the configured runner:

```powershell
python tools/run_gherkin_scenario.py smoke test_user_logs_in_with_valid_credentials
```

Each pytest process writes output to `artifacts/<run-id>/<scenario-name>/`. A failed scenario's
folder contains `scenario.log`, `screenshot.png`, `trace.zip`, and a `video/` directory when
those artifacts are enabled. Previous framework-generated run folders are removed automatically
at the start of each pytest run so stale outputs cannot be mistaken for the current result.

Create a clean source ZIP for distribution with:

```powershell
python tools/create_distribution.py
```

The archive is written under `dist/` and excludes credentials, Git metadata, virtual environments,
Allure results, caches, and generated test output.

## Notes

- Browser lifecycle remains controlled by pytest fixtures.
- Headed Chromium opens maximized with a screen-sized viewport at the browser's default 100% zoom; other browsers avoid Chromium-only launch flags.
- Page objects hold locators and user workflows.
- Step definitions stay thin and business-facing.
- Artifacts are configured under `artifacts/` and can be ignored by Git.
