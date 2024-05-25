import unittest
from unittest.mock import patch, mock_open, MagicMock
import uuid
from main import ProjectManagementSystem


class TestProjectManagementSystem(unittest.TestCase):

    @patch('builtins.open', new_callable=mock_open, read_data='{"users": [], "projects": []}')
    @patch('os.path.exists', return_value=True)
    def test_load_data(self, mock_exists, mock_open):
        pms = ProjectManagementSystem()
        self.assertEqual(pms.data, {"users": [], "projects": []})
        mock_open.assert_called_once_with('data.json', 'r')

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_data(self, mock_json_dump, mock_open):
        pms = ProjectManagementSystem()
        data = {"users": [{"username": "test"}], "projects": []}
        pms.save_data(data)
        mock_open.assert_called_once_with('data.json', 'w')
        mock_json_dump.assert_called_once_with(data, mock_open(), indent=4)

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

