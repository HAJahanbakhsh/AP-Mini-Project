import json
import os
import logging
import platform
import msvcrt
import re
import uuid
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from enum import Enum
import bcrypt


def getch():
    print("\nPress any key to continue...")
    if platform.system() == "Windows":
        msvcrt.getch()
    else:
        os.system('read -n 1 -s -r -p ""')


def cls():
    os.system('cls' if os.name == 'nt' else 'clear')


logging.basicConfig(
    filename='project_management.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

console = Console()


class Priority(Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class Status(Enum):
    BACKLOG = "BACKLOG"
    TODO = "TODO"
    DOING = "DOING"
    DONE = "DONE"
    ARCHIVED = "ARCHIVED"


class HistoryManager:
    def __init__(self, history_file='history.json'):
        self.history_file = history_file
        if not os.path.exists(self.history_file):
            with open(self.history_file, 'w') as file:
                json.dump({}, file)

    def add_history(self, task_id, user, action):
        with open(self.history_file, 'r') as file:
            history_data = json.load(file)

        if task_id not in history_data:
            history_data[task_id] = []

        timestamp = datetime.now().isoformat()
        history_data[task_id].append({
            "user": user,
            "action": action,
            "timestamp": timestamp
        })

        with open(self.history_file, 'w') as file:
            json.dump(history_data, file, indent=4)

    def get_history(self, task_id):
        with open(self.history_file, 'r') as file:
            history_data = json.load(file)

        return history_data.get(task_id, [])


class User:
    def __init__(self, email, username, password, active=True):
        self.email = email
        self.username = username
        self.password = password
        self.active = active

    @staticmethod
    def register():
        data = ProjectManagementSystem.load_data()
        email = input("Email: ")
        username = input("Username: ")
        password = input("Password: ")

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            console.print("Invalid email format. Please enter a valid email address.", style="bold red")
            getch()
            return

        for user in data["users"]:
            if user["email"] == email or user["username"] == username:
                console.print("Email or username already exists.", style="bold red")
                logger.warning("Attempt to register with existing email or username: %s, %s", email, username)
                getch()
                return

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(email, username, hashed_password)
        data["users"].append(new_user.__dict__)
        ProjectManagementSystem.save_data(data)
        console.print("User account created successfully.", style="bold green")
        getch()
        logger.info("New user registered: %s", username)

    @staticmethod
    def login():
        data = ProjectManagementSystem.load_data()
        username = input("Username: ")
        password = input("Password: ")

        for user_data in data["users"]:
            if user_data["username"] == username and bcrypt.checkpw(password.encode('utf-8'), user_data["password"].encode('utf-8')):
                if not user_data["active"]:
                    console.print("Your account is inactive.", style="bold red")
                    logger.warning("Inactive account login attempt: %s", username)
                    getch()
                    return None
                console.print("Login successful.", style="bold green")
                logger.info("User logged in: %s", username)
                getch()
                return User(**user_data)

        console.print("Incorrect username or password.", style="bold red")
        logger.warning("Failed login attempt: %s", username)
        getch()
        return None


class Task:
    def __init__(self, title, description, start_time, end_time, priority=Priority.LOW.value, status=Status.BACKLOG.value):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.start_time = start_time
        self.end_time = end_time
        self.priority = priority
        self.status = status
        self.assignees = []
        self.comments = []


class Project:
    def __init__(self, name, owner):
        self.id = str(uuid.uuid4())
        self.name = name
        self.owner = owner
        self.tasks = []
        self.members = [owner]

    def add_member(self, username):
        if username not in self.members:
            self.members.append(username)

    def create_task(self, title, description, start_time, end_time):
        new_task = Task(title, description, start_time, end_time)
        self.tasks.append(new_task.__dict__)
        return new_task


class ProjectManagementSystem:
    def __init__(self):
        self.data = self.load_data()

    @staticmethod
    def load_data():
        if os.path.exists('data.json'):
            with open('data.json', 'r') as file:
                return json.load(file)
        return {"users": [], "projects": []}

    @staticmethod
    def save_data(data):
        with open('data.json', 'w') as file:
            json.dump(data, file, indent=4)

    def main_menu(self):
        while True:
            cls()
            console.print("[bold blue]Project Management System[/bold blue]")
            console.print("1. Register")
            console.print("2. Login")

            choice = input("Enter your choice: ")
            if choice == "1":
                User.register()
            elif choice == "2":
                user = User.login()
                if user:
                    self.user_menu(user)
            else:
                console.print("Invalid choice.", style="bold red")
                getch()

    def user_menu(self, user):
        while True:
            cls()
            console.print(f"[bold blue]Welcome, {user.username}[/bold blue]")
            console.print("1. Create Project")
            console.print("2. View Projects")
            console.print("3. Logout")

            choice = input("Enter your choice: ")
            if choice == "1":
                self.create_project(user)
                getch()
            elif choice == "2":
                self.list_projects(user)
            elif choice == "3":
                break
            else:
                console.print("Invalid choice.", style="bold red")
                getch()

    def create_project(self, user):
        project_name = input("Project Name: ")
        new_project = Project(project_name, user.username)
        self.data["projects"].append(new_project.__dict__)
        self.save_data(self.data)
        console.print("Project created successfully.", style="bold green")
        logger.info("Project created: %s by %s", project_name, user.username)
        
        
    def list_projects(self, user):
        table = Table(title="Projects")
        table.add_column("Project Name", justify="center")
        table.add_column("Role", justify="center")

        user_projects = [project for project in self.data["projects"] if project["owner"] == user.username or user.username in project["members"]]

        for project in user_projects:
            role = "Member"
            if project["owner"] == user.username:
                role = "Owner"
            table.add_row(project["name"], role)

        console.print(table)
        project_name = input("Enter project name (or 'back' to go back): ")
        if project_name == "back":
            return

        for project in user_projects:
            if project["name"] == project_name:
                self.project_menu(user, project)
                break

    def project_menu(self, user, project):
        while True:
            cls()
            console.print(f"[bold blue]Project: {project['name']}[/bold blue]")
            console.print("1. Add Member")
            console.print("2. Delete Project")
            console.print("3. Manage Tasks")
            console.print("4. Back")

            choice = input("Enter your choice: ")
            if choice == "1":
                self.add_member(user, project)
                getch()
            elif choice == "2":
                self.delete_project(user, project)
                break
            elif choice == "3":
                self.manage_tasks(user, project)
            elif choice == "4":
                break
            else:
                console.print("Invalid choice.", style="bold red")
                getch()

    def add_member(self, user, project):
        if project["owner"] != user.username:
            console.print("Only the project owner can add members.", style="bold red")
            return

        username = input("Enter new member username: ")

        for member in project["members"]:
            if member == username:
                console.print("The user is already a member of the project.", style="bold red")
                return

        for u in self.data["users"]:
            if u["username"] == username:
                project["members"].append(username)
                self.save_data(self.data)
                console.print("New member added successfully.", style="bold green")
                return

        console.print("User not found.", style="bold red")

    def delete_project(self, user, project):
        if project["owner"] != user.username:
            console.print("Only the project owner can delete the project.", style="bold red")
            return

        self.data["projects"] = [p for p in self.data["projects"] if p["id"] != project["id"]]
        self.save_data(self.data)
        console.print("Project deleted successfully.", style="bold green")
        logger.info("Project deleted: %s by %s", project["name"], user.username)

    def manage_tasks(self, user, project):
        while True:
            cls()
            console.print(f"[bold blue]Manage Tasks for Project: {project['name']}[/bold blue]")
            console.print("1. Create Task")
            console.print("2. View Tasks")
            console.print("3. Back")

            choice = input("Enter your choice: ")
            if choice == "1":
                self.create_task(user, project)
                getch()
            elif choice == "2":
                self.list_tasks(user, project)
            elif choice == "3":
                break
            else:
                console.print("Invalid choice.", style="bold red")
                getch()

    def create_task(self, user, project):
        if user.username != project["owner"]:
            console.print("Only the project owner can create tasks.", style="bold red")
            logger.warning("Unauthorized task creation attempt by %s on project %s", user.username, project["name"])
            getch()
            return

        task_id = str(uuid.uuid4())
        title = input("Task Title: ")
        description = input("Task Description: ")
        start_time = datetime.now().isoformat()
        end_time = (datetime.now() + timedelta(hours=24)).isoformat()
        priority = Priority.LOW.value
        status = Status.BACKLOG.value
        
        new_task = {
            "id": task_id,
            "title": title,
            "description": description,
            "start_time": start_time,
            "end_time": end_time,
            "assignees": [],
            "priority": priority,
            "status": status,
            "comments": [],
            
        }

        project["tasks"].append(new_task)
        self.save_data(self.data)
        console.print("Task created successfully.", style="bold green")
        logger.info("Task created: %s in project %s by %s", title, project["name"], user.username)

    def list_tasks(self, user, project):
        table = Table(title=f"Tasks for Project: {project['name']}")
        table.add_column("Task Title", justify="center")
        table.add_column("Status", justify="center")
        table.add_column("Priority", justify="center")
        table.add_column("Start Time", justify="center")
        table.add_column("End Time", justify="center")

        for task in project["tasks"]:
            table.add_row(task["title"], task["status"], task["priority"], task["start_time"], task["end_time"])

        cls()
        console.print(table)
        task_title = input("Enter task title (or 'back' to go back): ")
        if task_title == "back":
            return

        for task in project["tasks"]:
            if task["title"] == task_title:
                self.task_menu(user, project, task)
                break

    def task_menu(self, user, project, task):
        while True:
            cls()
            console.print(f"[bold blue]Task: {task['title']}[/bold blue]")
            console.print("1. Change Status")
            console.print("2. Change Priority")
            console.print("3. Add Comment")
            console.print("4. Assign Member")
            console.print("5. View Comments")
            console.print("6. Back")

            choice = input("Enter your choice: ")
            if choice == "1":
                self.change_status(user, project, task)
                getch()
            elif choice == "2":
                self.change_priority(user, project, task)
                getch()
            elif choice == "3":
                self.add_comment(user, project, task)
                getch()
            elif choice == "4":
                self.assign_member_to_task(user, project, task)
                getch()
            elif choice == "5":
                self.view_comments(task)
                getch()
            elif choice == "6":
                break
            else:
                console.print("Invalid choice.", style="bold red")
                getch()

    def change_status(self, user, project, task):
        if user.username != project["owner"] and user.username not in task["assignees"]:
            console.print("Only the project owner or assigned members can change the task status.", style="bold red")
            logger.warning("Unauthorized status change attempt by %s on task %s in project %s", user.username,task["title"], project["name"])
            return

        console.print("Available statuses: BACKLOG, TODO, DOING, DONE, ARCHIVED")
        new_status = input("Enter new status: ").upper()
        if new_status in Status.__members__:
            task["status"] = new_status
            self.history_manager.add_history(task['id'], user.username, f"Changed status to {new_status}")
            self.save_data(self.data)
            console.print("Task status updated successfully.", style="bold green")
            logger.info("Status of task %s in project %s changed to %s by %s", task["title"], project["name"],new_status, user.username)
        else:
            console.print("Invalid status.", style="bold red")

    def change_priority(self, user, project, task):
        if user.username != project["owner"] and user.username not in task["assignees"]:
            console.print("Only the project owner or assigned members can change the task priority.", style="bold red")
            logger.warning("Unauthorized priority change attempt by %s on task %s in project %s", user.username,task["title"], project["name"])
            return

        console.print("Available priorities: CRITICAL, HIGH, MEDIUM, LOW")
        new_priority = input("Enter new priority: ").upper()
        if new_priority in Priority.__members__:
            task["priority"] = new_priority
            self.history_manager.add_history(task['id'], user.username, f"Changed priority to {new_priority}")
            self.save_data(self.data)
            console.print("Task priority updated successfully.", style="bold green")
            logger.info("Priority of task %s in project %s changed to %s by %s", task["title"], project["name"],new_priority, user.username)
        else:
            console.print("Invalid priority.", style="bold red")

    def add_comment(self, user, project, task):
        comment = input("Enter your comment: ")
        new_comment = {
            "username": user.username,
            "comment": comment,
            "timestamp": datetime.now().isoformat()
        }
        task["comments"].append(new_comment)
        self.history_manager.add_history(task['id'],user.username, f"add new comment: {new_comment['comment']}")
        self.save_data(self.data)
        console.print("Comment added successfully.", style="bold green")
        logger.info("Comment added to task %s in project %s by %s", task["title"], project["name"], user.username)

    def assign_member_to_task(self, user, project, task):
        if user.username != project["owner"]:
            console.print("Only the project owner can assign members to tasks.", style="bold red")
            logger.warning("Unauthorized member assignment attempt by %s on task %s in project %s", user.username,task["title"], project["name"])
            return

        assignee = input("Enter username of the member to assign: ")
        if assignee in project["members"]:
            if assignee not in task["assignees"]:
                task["assignees"].append(assignee)
                self.history_manager.add_history(task['id'], user.username, f"Assigned member {assignee}")
                self.save_data(self.data)
                console.print("Member assigned to task successfully.", style="bold green")
                logger.info("Member %s assigned to task %s in project %s by %s", assignee, task["title"],project["name"], user.username)
            else:
                console.print("Member is already assigned to this task.", style="bold red")
        else:
            console.print("User is not a member of this project.", style="bold red")

    @staticmethod
    def view_comments(task):
        if not task["comments"]:
            console.print("No comments available for this task.", style="bold red")
        else:
            for comment in task["comments"]:
                console.print(
                    f"[bold yellow]{comment['timestamp']} - {comment['username']}:[/bold yellow] {comment['comment']}")


if __name__ == "__main__":
    pms = ProjectManagementSystem()
    while True:
        pms.main_menu()














