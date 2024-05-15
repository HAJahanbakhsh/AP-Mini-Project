import json
import os
import re
import uuid
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from enum import Enum
import bcrypt

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
