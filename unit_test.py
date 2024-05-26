import unittest
from unittest.mock import patch, mock_open, MagicMock
import uuid
from datetime import datetime, timedelta
import re
import bcrypt
from main import ProjectManagementSystem , User


class TestProjectManagementSystem(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data='{"users": [], "projects": []}')
    @patch('os.path.exists', return_value=True)
    def test_load_data(self, mock_exists, mock_open):
        pms = ProjectManagementSystem()
        self.assertEqual(pms.data, {"users": [], "projects": []})
        mock_open.assert_called_once_with('data.json', 'r')


    @patch('builtins.input', side_effect=['Test Project'])
    @patch.object(ProjectManagementSystem, 'save_data')
    def test_create_project(self, mock_save_data, mock_input):
        pms = ProjectManagementSystem()
        user = MagicMock(username='testuser')
        pms.data = {"users": [{"username": "testuser"}], "projects": []}

        pms.create_project(user)

        self.assertEqual(len(pms.data["projects"]), 1)
        self.assertEqual(pms.data["projects"][0]["name"], "Test Project")
        self.assertEqual(pms.data["projects"][0]["owner"], "testuser")
        mock_save_data.assert_called_once()

    @patch('builtins.input', side_effect=['newmember'])
    @patch.object(ProjectManagementSystem, 'save_data')
    def test_add_member(self, mock_save_data, mock_input):
        pms = ProjectManagementSystem()
        user = MagicMock(username='owner')
        project = {"name": "Test Project", "owner": "owner", "members": [], "tasks": []}
        pms.data = {"users": [{"username": "newmember"}], "projects": [project]}

        pms.add_member(user, project)

        self.assertIn("newmember", project["members"])
        mock_save_data.assert_called_once()

    @patch('builtins.input', side_effect=['Test Task', 'Task Description'])
    @patch.object(ProjectManagementSystem, 'save_data')
    @patch('uuid.uuid4', return_value=uuid.UUID('12345678123456781234567812345678'))
    def test_create_task(self, mock_uuid, mock_save_data, mock_input):
        pms = ProjectManagementSystem()
        user = MagicMock(username='owner')
        project = {"name": "Test Project", "owner": "owner", "members": [], "tasks": []}
        pms.data = {"users": [{"username": "owner"}], "projects": [project]}

        pms.create_task(user, project)

        self.assertEqual(len(project["tasks"]), 1)
        self.assertEqual(project["tasks"][0]["title"], "Test Task")
        self.assertEqual(project["tasks"][0]["description"], "Task Description")
        self.assertEqual(project["tasks"][0]["id"], '12345678-1234-5678-1234-567812345678')
        mock_save_data.assert_called_once()


class TestUser(unittest.TestCase):

    @patch('builtins.input', side_effect=['testuser', 'password123'])
    @patch.object(ProjectManagementSystem, 'load_data', return_value={
        "users": [{"email": "test@example.com", "username": "testuser", "password": bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), "active": True}]
    })
    def test_login_success(self, mock_load_data, mock_input):
        user = User.login()
        self.assertIsNotNone(user)
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "test@example.com")

    @patch('builtins.input', side_effect=['testuser', 'wrongpassword'])
    @patch.object(ProjectManagementSystem, 'load_data', return_value={
        "users": [{"email": "test@example.com", "username": "testuser", "password": bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), "active": True}]
    })
    def test_login_incorrect_password(self, mock_load_data, mock_input):
        user = User.login()
        self.assertIsNone(user)

    @patch('builtins.input', side_effect=['inactiveuser', 'password123'])
    @patch.object(ProjectManagementSystem, 'load_data', return_value={
        "users": [{"email": "inactive@example.com", "username": "inactiveuser", "password": bcrypt.hashpw('password123'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8'), "active": False}]
    })
    def test_login_inactive_user(self, mock_load_data, mock_input):
        user = User.login()
        self.assertIsNone(user)


if __name__ == '__main__':
    unittest.main()
