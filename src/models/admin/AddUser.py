

from dataclasses import dataclass


@dataclass
class AddUser:
    user_role: str
    employee_name: str
    status: str
    username: str
    password: str