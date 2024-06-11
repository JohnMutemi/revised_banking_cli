import sqlite3
import uuid

CONN = sqlite3.connect('bank.db')
CURSOR = CONN.cursor()

class User:
    def __init__(self, username, pin):
        self.id = str(uuid.uuid4())
        self.username = username
        self.pin = pin
        self.balance = 0.0

    @classmethod
    def create_table(cls):
        CURSOR.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                pin TEXT NOT NULL,
                balance REAL NOT NULL
            )
        ''')
        CONN.commit()

    def save(self):
        CURSOR.execute('INSERT INTO users (id, username, pin, balance) VALUES (?, ?, ?, ?)',
                       (self.id, self.username, self.pin, self.balance))
        CONN.commit()

    @classmethod
    def find_by_id(cls, user_id):
        CURSOR.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user_data = CURSOR.fetchone()
        if user_data:
            user = cls(user_data[1], user_data[2])
            user.id = user_data[0]
            user.balance = user_data[3]
            return user
        return None

    @classmethod
    def find_by_username(cls, username):
        CURSOR.execute('SELECT * FROM users WHERE username = ?', (username,))
        user_data = CURSOR.fetchone()
        if user_data:
            user = cls(user_data[1], user_data[2])
            user.id = user_data[0]
            user.balance = user_data[3]
            return user
        return None

    @classmethod
    def get_all(cls):
        CURSOR.execute('SELECT * FROM users')
        return CURSOR.fetchall()

    def update_balance(self, amount):
        self.balance += amount
        CURSOR.execute('UPDATE users SET balance = ? WHERE id = ?', (self.balance, self.id))
        CONN.commit()

    def delete(self):
        CURSOR.execute('DELETE FROM users WHERE id = ?', (self.id,))
        CONN.commit()

class Transaction:
    def __init__(self, user_id, amount, type):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.amount = amount
        self.type = type

    @classmethod
    def create_table(cls):
        CURSOR.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                amount REAL NOT NULL,
                type TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        ''')
        CONN.commit()

    def save(self):
        CURSOR.execute('INSERT INTO transactions (id, user_id, amount, type) VALUES (?, ?, ?, ?)',
                       (self.id, self.user_id, self.amount, self.type))
        CONN.commit()

    @classmethod
    def find_by_id(cls, transaction_id):
        CURSOR.execute('SELECT * FROM transactions WHERE id = ?', (transaction_id,))
        transaction_data = CURSOR.fetchone()
        if transaction_data:
            transaction = cls(transaction_data[1], transaction_data[2], transaction_data[3])
            transaction.id = transaction_data[0]
            return transaction
        return None

    @classmethod
    def find_by_user_id(cls, user_id):
        CURSOR.execute('SELECT * FROM transactions WHERE user_id = ?', (user_id,))
        return CURSOR.fetchall()

    @classmethod
    def get_all(cls):
        CURSOR.execute('SELECT * FROM transactions')
        return CURSOR.fetchall()

    def delete(self):
        CURSOR.execute('DELETE FROM transactions WHERE id = ?', (self.id,))
        CONN.commit()

class BankATM:
    def __init__(self):
        User.create_table()
        Transaction.create_table()

    def login(self):
        username = input("Enter your username: ")
        pin = input("Enter your pin: ")
        user = User.find_by_username(username)
        if user and user.pin == pin:
            return user.id
        else:
            print("Invalid username or pin.")
            return None

    def create_user(self):
        username = input("Enter a new username: ")
        pin = input("Enter a new pin: ")
        user = User(username, pin)
        user.save()
        print(f"User created with ID {user.id}")

    def delete_user(self, user_id):
        user = User.find_by_id(user_id)
        if user:
            user.delete()
            print("User deleted successfully.")
        else:
            print("User not found.")

    def deposit(self, user_id):
        user = User.find_by_id(user_id)
        if user:
            amount = float(input("Enter amount to deposit: "))
            user.update_balance(amount)
            transaction = Transaction(user_id, amount, "deposit")
            transaction.save()
            print(f"Deposited {amount}. New balance is {user.balance}.")
        else:
            print("User not found.")

    def withdraw(self, user_id):
        user = User.find_by_id(user_id)
        if user:
            amount = float(input("Enter amount to withdraw: "))
            if user.balance >= amount:
                user.update_balance(-amount)
                transaction = Transaction(user_id, amount, "withdraw")
                transaction.save()
                print(f"Withdrew {amount}. New balance is {user.balance}.")
            else:
                print("Insufficient funds.")
        else:
            print("User not found.")

    def view_balance(self, user_id):
        user = User.find_by_id(user_id)
        if user:
            print(f"Current balance: {user.balance}")
        else:
            print("User not found.")

    def pay_bill(self, user_id):
        user = User.find_by_id(user_id)
        if user:
            bill_type = input("Enter bill type (electric, water, gas): ").lower()
            amount = float(input(f"Enter amount to pay for {bill_type} bill: "))
            if user.balance >= amount:
                user.update_balance(-amount)
                transaction = Transaction(user_id, amount, f"pay_{bill_type}_bill")
                transaction.save()
                print(f"Paid {amount} for {bill_type} bill. New balance is {user.balance}.")
            else:
                print("Insufficient funds.")
        else:
            print("User not found.")
