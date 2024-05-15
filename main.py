import json
import os
import re
import uuid
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from enum import Enum
import bcrypt

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
            return

        for user in data["users"]:
            if user["email"] == email or user["username"] == username:
                console.print("Email or username already exists.", style="bold red")
                return

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        new_user = User(email, username, hashed_password)
        data["users"].append(new_user.__dict__)
        ProjectManagementSystem.save_data(data)
        console.print("User account created successfully.", style="bold green")
        

    @staticmethod
    def login():
        data = ProjectManagementSystem.load_data()
        username = input("Username: ")
        password = input("Password: ")

        for user_data in data["users"]:
            if user_data["username"] == username and bcrypt.checkpw(password.encode('utf-8'), user_data["password"].encode('utf-8')):
                if not user_data["active"]:
                    console.print("Your account is inactive.", style="bold red")
                    return None
                console.print("Login successful.", style="bold green")
                return User(**user_data)

        console.print("Incorrect username or password.", style="bold red")
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


    def user_menu(self, user):
        while True:
            console.print(f"[bold blue]Welcome, {user.username}[/bold blue]")
            console.print("1. Create Project")
            console.print("2. View Projects")
            console.print("3. Logout")

            choice = input("Enter your choice: ")
            if choice == "1":
                self.create_project(user)
            elif choice == "2":
                self.list_projects(user)
            elif choice == "3":
                break
            else:
                console.print("Invalid choice.", style="bold red")

    def create_project(self, user):
        project_name = input("Project Name: ")
        new_project = Project(project_name, user.username)
        self.data["projects"].append(new_project.__dict__)
        self.save_data(self.data)
        console.print("Project created successfully.", style="bold green")






