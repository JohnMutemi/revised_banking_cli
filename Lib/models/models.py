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
        self._pin = None
        self.pin = pin
        self.balance = 0.0  # Initialize balance to 0
        self.id = id
    @property
    def pin(self):
        return self._pin

    @pin.setter
    def pin(self, value):
        if isinstance(value, int) and len(str(value)) == 4:
            self._pin = value
        else:
            raise ValueError('Pin must be a 4-digit number!')
    @classmethod
    def create_table(cls):
        # Creates the users table if it does not exist.
        CURSOR.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                pin INTEGER,
                balance REAL
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
    def __init__(self, user_id, amount, transaction_type, category_id, username,id=None):
        self.user_id = user_id
        self.amount = amount
        self.transaction_type = transaction_type
        self.category_id = category_id
        self.id = id
        self.username=username

    @classmethod
    def create_table(cls):
        # Creates the transactions table if it does not exist.
        with CONN:
            CONN.execute('''
                CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    amount REAL,
                    transaction_type TEXT,
                    category_id INTEGER,
                    username TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id),
                    FOREIGN KEY (category_id) REFERENCES transaction_categories(id)
                )
            ''')

    def save(self):
        # Inserts the transaction into the database and updates the transaction ID.
        with CONN:
            CONN.execute('INSERT INTO transactions (user_id, amount, transaction_type, category_id, username) VALUES (?, ?, ?, ?, ?)',
                       (self.user_id, self.amount, self.transaction_type, self.category_id, self.username))
            self.id = CURSOR.lastrowid  # Get the ID of the newly inserted row

    @classmethod
    def find_by_id(cls, transaction_id):
        # Finds a transaction by its ID.
        CURSOR.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
        transaction_data = CURSOR.fetchone()  # Fetch one result
        if transaction_data:
            transaction = cls(transaction_data[1], transaction_data[2], transaction_data[3], transaction_data[4])  # Create a Transaction instance
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
        with CONN:
            CONN.execute('DELETE FROM transactions WHERE id = ?', (self.id,))
    @classmethod
    def get_transactions_by_user_id(cls, user_id):
        # Fetches all transactions for a given user ID.
        CURSOR.execute('''
            SELECT transactions.id, users.username, transactions.amount, transactions.transaction_type, transaction_categories.name, transactions.timestamp
            FROM transactions
            JOIN users ON transactions.user_id = users.id
            JOIN transaction_categories ON transactions.category_id = transaction_categories.id
            WHERE transactions.user_id = ?
            ORDER BY transactions.timestamp DESC
        ''', (user_id,))
        return CURSOR.fetchall()

class TransactionCategory:
    @classmethod
    def create_table(cls):
        # Creates the transaction_categories table if it does not exist.
        with CONN:
            CONN.execute('''
                CREATE TABLE IF NOT EXISTS transaction_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    description TEXT
                )
            ''')
    @classmethod
    def create_default_transaction_categories(cls):
        # Creates default transaction categories if they do not exist.
        with CONN:
            CONN.execute('INSERT OR IGNORE INTO transaction_categories (name, description) VALUES (?, ?)', ('Deposit', 'Deposit transaction'))
            CONN.execute('INSERT OR IGNORE INTO transaction_categories (name, description) VALUES (?, ?)', ('Withdrawal', 'Withdrawal transaction'))
            CONN.execute('INSERT OR IGNORE INTO transaction_categories (name, description) VALUES (?, ?)', ('Bill Payment', 'Bill payment transaction'))
    @classmethod
    def get_all(cls):
        # Returns a list of all transaction categories.
        CURSOR.execute('SELECT * FROM transaction_categories')
        return CURSOR.fetchall()  # Fetch all results

    @classmethod
    def get_category_id_by_name(cls, category_name):
        # Fetches the category ID by the category name.
        CURSOR.execute('SELECT id FROM transaction_categories WHERE name = ?', (category_name,))
        category = CURSOR.fetchone()
        if category:
            return category[0]
        return None
class BankATM:
    def __init__(self):
        # Initializes the BankATM by creating the necessary tables."""
        User.create_table()
        Transaction.create_table()
        TransactionCategory.create_table()
        TransactionCategory.create_default_transaction_categories()

    # Methods for managing transaction categories
    def create_transaction_category(self):
        # Creates a new transaction category."""
        name = input(Fore.CYAN + "Enter transaction category name: ")
        description = input(Fore.CYAN + "Enter transaction category description: ")
        with CONN:
            CONN.execute('INSERT INTO transaction_categories (name, description) VALUES (?, ?)', (name, description))
        print(Fore.GREEN + "Transaction category created successfully.")

    def view_transaction_categories(self):
        # Displays all transaction categories."""
        transaction_categories = TransactionCategory.get_all()
        if transaction_categories:
            print(Fore.GREEN + "Transaction Categories:")
            for cat in transaction_categories:
                print(f"ID: {cat[0]}, Name: {cat[1]}, Description: {cat[2]}")
        else:
            print(Fore.RED + "No transaction categories found.")
    def view_transactions(self, user_id):
        # Displays all transactions for the logged-in user."""
        transactions = Transaction.get_transactions_by_user_id(user_id)
        if transactions:
            print(Fore.GREEN + "Transactions:")
            for trans in transactions:
                print(f"ID: {trans[0]}, Username: {trans[1]}, Amount: {trans[2]}, Type: {trans[3]}, Category: {trans[4]}, Timestamp: {trans[5]}")
        else:
            print(Fore.RED + "No transactions found.")

    def get_valid_input(self, prompt, type_func):
        while True:
            try:
                return type_func(input(prompt))
            except ValueError:
                print(Fore.RED + "Invalid input. Please try again.")
    # Handle login
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
    # Create a user
    def create_user(self):
        username = input(Fore.CYAN + "Enter a new username: ")
        pin = self.get_valid_input(Fore.CYAN + "Enter a new pin: ", int)
        user = User(username, pin)
        user.save()
        print(Fore.GREEN + f"Welcome {username}! Press 2 to login")
    # delete a user
    def delete_user(self, user_id):
        try:
            with CONN:
                # Check if the user exists
                CURSOR.execute('SELECT * FROM users WHERE id = ?', (user_id,))
                user = CURSOR.fetchone()
                if user:
                    # First delete all related transactions
                    CONN.execute('DELETE FROM transactions WHERE user_id = ?', (user_id,))
                    # Then delete the user
                    CONN.execute('DELETE FROM users WHERE id = ?', (user_id,))
                    print(Fore.GREEN + "Account deleted successfully.")
                else:
                    print(Fore.RED + "User not found.")
        except sqlite3.Error as e:
            print(Fore.RED + f"An error occurred: {e}")
    # Handle deposit transactions
    def deposit(self, user_id):
        user = User.find_by_id(user_id)
        if user:
            amount = self.get_valid_input(Fore.CYAN + "Enter amount to deposit: ", float)
            for _ in tqdm(range(100), desc="Processing deposit", ascii=False, ncols=75):
                time.sleep(0.01)  # Simulate processing time    
            user.update_balance(amount)
            category_id = TransactionCategory.get_category_id_by_name('Deposit')
            username = self.get_username_by_user_id(user_id)  # Fetch the username
            transaction = Transaction(user_id, amount, "deposit", category_id, username)
            transaction.save()
            print(Fore.GREEN + f"Deposited {amount}. New balance is {user.balance}.")
        else:
            print(Fore.RED + "User not found.")
    # Handle withdrawal transactions
    def withdraw(self, user_id):
        user = User.find_by_id(user_id)
        if user:
            amount = self.get_valid_input(Fore.CYAN + "Enter amount to withdraw: ", float)
            if user.balance >= amount:
                for _ in tqdm(range(100), desc="Processing withdrawal", ascii=False, ncols=75):
                    time.sleep(0.01)  # Simulate processing time
                user.update_balance(-amount)
                category_id = TransactionCategory.get_category_id_by_name('Withdrawal')
                username = self.get_username_by_user_id(user_id)
                transaction = Transaction(user_id, amount, "withdrawal", category_id, username)
                transaction.save()
                print(Fore.GREEN + f"Withdrew {amount}. New balance is {user.balance}.")
            else:
                print(Fore.RED + "Insufficient funds.")
        else:
            print(Fore.RED + "User not found.")
    # enable user to view their current balance
    def view_balance(self, user_id):
        user = User.find_by_id(user_id)
        if user:
            print(Fore.GREEN + f"Current balance: {user.balance}")
        else:
            print(Fore.RED + "User not found.")
    # Handle bill payment transactions 
    def pay_bill(self, user_id):
        user = User.find_by_id(user_id)
        if user:
            bill_type = input(Fore.CYAN + "Enter bill type (fees, rent, vacation): ").lower()
            amount = self.get_valid_input(Fore.CYAN + f"Enter amount to pay for {bill_type} bill: ", float)
            if user.balance >= amount:
                for _ in tqdm(range(100), desc=f"Processing {bill_type} bill payment", ascii=False, ncols=75):
                    time.sleep(0.01)  # Simulate processing time
                user.update_balance(-amount)
                category_id = TransactionCategory.get_category_id_by_name('Bill Payment')
                username = self.get_username_by_user_id(user_id)
                transaction = Transaction(user_id, amount, f"pay_{bill_type}_bill", category_id, username)
                transaction.save()
                print(Fore.GREEN + f"Paid {amount} for {bill_type} bill. New balance is {user.balance}.")
            else:
                print(Fore.RED + "Insufficient funds.")
        else:
            print(Fore.RED + "User not found.")

    # Fetch the username for a given user ID.
    def get_username_by_user_id(self, user_id):
        CURSOR.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        user = CURSOR.fetchone()
        if user:
            return user[0]
        return None
