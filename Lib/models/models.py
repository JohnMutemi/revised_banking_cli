import sqlite3
from colorama import init, Fore, Style
from tqdm import tqdm
import time

# Initialize colorama
init(autoreset=True)

# Establish a connection to the SQLite database and create a cursor object
CONN = sqlite3.connect('bank.db')
CURSOR = CONN.cursor()

# Enable foreign key constraints
CURSOR.execute('PRAGMA foreign_keys = ON;')

class User:
    def __init__(self, username, pin, id=None):
        self.username = username
        self.pin = pin
        self.balance = 0.0  # Initialize balance to 0
        self.id = id

    @classmethod
    def create_table(cls):
        """Creates the users table if it does not exist."""
        CURSOR.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                pin INTEGER NOT NULL,
                balance REAL NOT NULL
            )
        ''')
        CONN.commit()  # Save the changes

    def save(self):
        # Inserts the user into the database and updates the user ID.
        CURSOR.execute('INSERT INTO users (username, pin, balance) VALUES (?, ?, ?)',
                       (self.username, self.pin, self.balance))
        self.id = CURSOR.lastrowid  # Get the ID of the newly inserted row
        CONN.commit()  # Save the changes

    @classmethod
    def find_by_id(cls, user_id):
        # Finds a user by their ID.
        CURSOR.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_data = CURSOR.fetchone()  # Fetch one result
        if user_data:
            user = cls(user_data[1], user_data[2])  # Create a User instance with fetched data
            user.id = user_data[0]
            user.balance = user_data[3]
            return user
        return None

    @classmethod
    def find_by_username(cls, username):
        # Finds a user by their username.
        CURSOR.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_data = CURSOR.fetchone()  # Fetch one result
        if user_data:
            user = cls(user_data[1], user_data[2])  # Create a User instance with fetched data
            user.id = user_data[0]
            user.balance = user_data[3]
            return user
        return None

    @classmethod
    def get_all(cls):
        # Returns a list of all users.
        CURSOR.execute('SELECT * FROM users')
        return CURSOR.fetchall()  # Fetch all results

    def update_balance(self, amount):
        # Updates the user's balance by the specified amount.
        self.balance += amount
        CURSOR.execute('UPDATE users SET balance = ? WHERE id = ?', (self.balance, self.id))
        CONN.commit()  # Save the changes

    def delete(self):
        # Deletes the user from the database.
        CURSOR.execute('DELETE FROM users WHERE id = ?', (self.id,))
        CONN.commit()  # Save the changes

class Transaction:
    def __init__(self, user_id, amount, type, id=None):
        self.user_id = user_id
        self.amount = amount
        self.type = type
        self.id = id

    @classmethod
    def create_table(cls):
        # Creates the transactions table if it does not exist.
        CURSOR.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                type TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        CONN.commit()  # Save the changes

    def save(self):
        # Inserts the transaction into the database and updates the transaction ID.
        CURSOR.execute('INSERT INTO transactions (user_id, amount, type) VALUES (?, ?, ?)',
                       (self.user_id, self.amount, self.type))
        self.id = CURSOR.lastrowid  # Get the ID of the newly inserted row
        CONN.commit()  # Save the changes

    @classmethod
    def find_by_id(cls, transaction_id):
        # Finds a transaction by its ID.
        CURSOR.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
        transaction_data = CURSOR.fetchone()  # Fetch one result
        if transaction_data:
            transaction = cls(transaction_data[1], transaction_data[2], transaction_data[3])  # Create a Transaction instance
            transaction.id = transaction_data[0]
            return transaction
        return None

    @classmethod
    def find_by_user_id(cls, user_id):
        # Finds all transactions for a given user ID.
        CURSOR.execute('SELECT * FROM transactions WHERE user_id = ?', (user_id,))
        return CURSOR.fetchall()  # Fetch all results for the given user_id

    @classmethod
    def get_all(cls):
        # Returns a list of all transactions.
        CURSOR.execute('SELECT * FROM transactions')
        return CURSOR.fetchall()  # Fetch all results

    def delete(self):
        # Deletes the transaction from the database.
        CURSOR.execute('DELETE FROM transactions WHERE id = ?', (self.id,))
        CONN.commit()  # Save the changes

class BankATM:
    def __init__(self):
        # Initializes the BankATM by creating the necessary tables.
        User.create_table()
        Transaction.create_table()

    def get_valid_input(self, prompt, type_func):
        while True:
            try:
                return type_func(input(prompt))
            except ValueError:
                print(Fore.RED + "Invalid input. Please try again.")

    def login(self):
        print(Fore.CYAN + "Enter your username: ", end="")
        username = input()
        print(Fore.CYAN + "Enter your pin: ", end="")
        pin = input()
        user = User.find_by_username(username)
        if user and user.pin == int(pin):
            return user.id
        else:
            print(Fore.RED + "Invalid username or pin.")
            return None

    def create_user(self):
        username = input(Fore.CYAN + "Enter a new username: ")
        pin = self.get_valid_input(Fore.CYAN + "Enter a new pin: ", int)
        user = User(username, pin)
        user.save()
        print(Fore.GREEN + f"Welcome {username}! Press 2 to login")

    def delete_user(self, user_id):
        user = User.find_by_id(user_id)
        if user:
            user.delete()
            print(Fore.GREEN + "User deleted successfully.")
        else:
            print(Fore.RED + "User not found.")

    def deposit(self, user_id):
        user = User.find_by_id(user_id)
        if user:
            amount = self.get_valid_input(Fore.CYAN + "Enter amount to deposit: ", float)
            for _ in tqdm(range(100), desc="Processing deposit", ascii=False, ncols=75):
                time.sleep(0.01)  # Simulate processing time
            user.update_balance(amount)
            transaction = Transaction(user_id, amount, "deposit")
            transaction.save()
            print(Fore.GREEN + f"Deposited {amount}. New balance is {user.balance}.")
        else:
            print(Fore.RED + "User not found.")

    def withdraw(self, user_id):
        user = User.find_by_id(user_id)
        if user:
            amount = self.get_valid_input(Fore.CYAN + "Enter amount to withdraw: ", float)
            if user.balance >= amount:
                for _ in tqdm(range(100), desc="Processing withdrawal", ascii=False, ncols=75):
                    time.sleep(0.01)  # Simulate processing time
                user.update_balance(-amount)
                transaction = Transaction(user_id, amount, "withdraw")
                transaction.save()
                print(Fore.GREEN + f"Withdrew {amount}. New balance is {user.balance}.")
            else:
                print(Fore.RED + "Insufficient funds.")
        else:
            print(Fore.RED + "User not found.")

    def view_balance(self, user_id):
        user = User.find_by_id(user_id)
        if user:
            print(Fore.GREEN + f"Current balance: {user.balance}")
        else:
            print(Fore.RED + "User not found.")

    def pay_bill(self, user_id):
        user = User.find_by_id(user_id)
        if user:
            bill_type = input(Fore.CYAN + "Enter bill type (fees, rent, vacation): ").lower()
            amount = self.get_valid_input(Fore.CYAN + f"Enter amount to pay for {bill_type} bill: ", float)
            if user.balance >= amount:
                for _ in tqdm(range(100), desc=f"Processing {bill_type} bill payment", ascii=False, ncols=75):
                    time.sleep(0.01)  # Simulate processing time
                user.update_balance(-amount)
                transaction = Transaction(user_id, amount, f"pay_{bill_type}_bill")
                transaction.save()
                print(Fore.GREEN + f"Paid {amount} for {bill_type} bill. New balance is {user.balance}.")
            else:
                print(Fore.RED + "Insufficient funds.")
        else:
            print(Fore.RED + "User not found.")
