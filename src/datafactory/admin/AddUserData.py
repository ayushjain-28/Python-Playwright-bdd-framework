from uuid import uuid4

from models.admin.AddUser import AddUser
from utilities.PythonHelper import PythonHelper

user_roles = ["Admin", "ESS"]
status_options = ["Enabled", "Disabled"]

def get_edit_admin_data() -> AddUser:
    unique_id = uuid4().hex[:10]
    return AddUser(
        user_role=PythonHelper.random_option(user_roles),
        employee_name=PythonHelper.get_random_alphabet(),
        status=PythonHelper.random_option(status_options),
        username=f"username{PythonHelper.timestamp_hhmmss()}_{unique_id}",
        password=f"Admin@{unique_id}9a",
    )


def get_new_admin_data() -> AddUser:
    unique_id = uuid4().hex[:10]
    return AddUser(
        user_role=PythonHelper.random_option(user_roles),
        employee_name=PythonHelper.get_random_alphabet(),
        status=PythonHelper.random_option(status_options),
        username=f"username{PythonHelper.timestamp_hhmmss()}_{unique_id}",
        password=f"Admin@{unique_id}9a",
    )
