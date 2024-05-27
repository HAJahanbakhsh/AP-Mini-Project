import argparse
import json
import os


def create_admin(username, password):
    if os.path.exists('admin.json'):
        print("Admin already exists.")
        return

    admin_data = {
        "username": username,
        "password": password
    }

    with open('admin.json', 'w') as admin_file:
        json.dump(admin_data, admin_file)

    print("Admin created successfully")


def load_users():
    if os.path.exists('data.json'):
        with open('data.json', 'r') as file:
            data = json.load(file)
            return data.get('users', [])
    return []


def save_users(users):
    data = {
        'users': users
    }
    with open('data.json', 'w') as file:
        json.dump(data, file)


def activate_user(username):
    users = load_users()
    for user in users:
        if user['username'] == username:
            user['active'] = True
            save_users(users)
            print(f"User {username} activated.")
            return
    print(f"User {username} not found.")


def deactivate_user(username):
    users = load_users()
    for user in users:
        if user['username'] == username:
            user['active'] = False
            save_users(users)
            print(f"User {username} deactivated.")
            return
    print(f"User {username} not found.")


def purge_data():
    if os.path.exists('data.json'):
        with open('data.json', 'w') as file:
            json.dump({'users': [], 'projects': []}, file)
        print("All data purged.")
    else:
        print("No data to purge.")    


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Admin Management")
    subparsers = parser.add_subparsers(dest='command')

    create_admin_parser = subparsers.add_parser('create-admin', help='Create admin account')
    create_admin_parser.add_argument('--username', required=True, help='Admin username')
    create_admin_parser.add_argument('--password', required=True, help='Admin password')

    activate_user_parser = subparsers.add_parser('activate-user', help='Activate a user account')
    activate_user_parser.add_argument('--username', required=True, help='Username to activate')

    deactivate_user_parser = subparsers.add_parser('deactivate-user', help='Deactivate a user account')
    deactivate_user_parser.add_argument('--username', required=True, help='Username to deactivate')

    purge_data_parser = subparsers.add_parser('purge-data', help='Purge all stored data')

    args = parser.parse_args()

    if args.command == 'create-admin':
        create_admin(args.username, args.password)
    elif args.command == 'activate-user':
        activate_user(args.username)
    elif args.command == 'deactivate-user':
        deactivate_user(args.username)
    elif args.command == 'purge-data':
        purge_data()    
    else:
        parser.print_help()



#python manager.py activate-user --username user1
#python manager.py create-admin --username admin --password adminpass
#python manager.py deactivate-user --username user1
#python3 manager.py purge-data
