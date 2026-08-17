import os
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from fastapi import HTTPException

from auth import authenticate, require_admin


class AuthenticationRoleTests(unittest.TestCase):
    def test_default_accounts_have_distinct_roles(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(authenticate("admin", "admin")["role"], "admin")
            self.assertEqual(authenticate("tester", "tester")["role"], "tester")

    def test_incorrect_password_is_rejected(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(authenticate("tester", "incorrect"))

    def test_environment_credentials_override_defaults(self):
        values = {
            "APP_USERNAME": "manager",
            "APP_PASSWORD": "manager-secret",
            "TESTER_USERNAME": "student",
            "TESTER_PASSWORD": "student-secret",
        }
        with patch.dict(os.environ, values, clear=True):
            self.assertEqual(authenticate("manager", "manager-secret")["role"], "admin")
            self.assertEqual(authenticate("student", "student-secret")["role"], "tester")
            self.assertIsNone(authenticate("admin", "admin"))

    def test_tester_cannot_pass_admin_authorization(self):
        request = SimpleNamespace(
            session={"logged_in": True, "username": "tester", "role": "tester"}
        )
        with self.assertRaises(HTTPException) as raised:
            require_admin(request)
        self.assertEqual(raised.exception.status_code, 403)

    def test_admin_passes_admin_authorization(self):
        request = SimpleNamespace(
            session={"logged_in": True, "username": "admin", "role": "admin"}
        )
        self.assertEqual(require_admin(request), "admin")


if __name__ == "__main__":
    unittest.main()
