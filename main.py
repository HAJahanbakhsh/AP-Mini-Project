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






