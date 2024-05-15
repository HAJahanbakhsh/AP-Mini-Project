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
