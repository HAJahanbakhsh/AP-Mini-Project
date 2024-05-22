import argparse
import json
import os


def create_admin(username, password):
    if os.path.exists('admin.json'):
        print("admin already exist")
        return

    admin_data = {
        "username": username,
        "password": password
    }

    with open('admin.json', 'w') as admin_file:
        json.dump(admin_data, admin_file)

    print("admin create successfully")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="admin")
    parser.add_argument("create-admin", help="create admin")
    parser.add_argument("--username", required=True, help="admin username")
    parser.add_argument("--password", required=True, help="admin password")
    args = parser.parse_args()

    if args.create_admin:
        create_admin(args.username, args.password)
