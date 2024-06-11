from models import  BankATM

def main():
    atm = BankATM()
    while True:
        print("\n--- Bank ATM ---")
        print("1. Create User")
        print("2. Login")
        print("3. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            atm.create_user()
        elif choice == "2":
            user_id = atm.login()
            if user_id:
                while True:
                    print("\n--- User Menu ---")
                    print("1. Deposit")
                    print("2. Withdraw")
                    print("3. View Balance")
                    print("4. Pay Bill")
                    print("5. Delete Account")
                    print("6. Logout")
                    user_choice = input("Choose an option: ")
                    if user_choice == "1":
                        atm.deposit(user_id)
                    elif user_choice == "2":
                        atm.withdraw(user_id)
                    elif user_choice == "3":
                        atm.view_balance(user_id)
                    elif user_choice == "4":
                        atm.pay_bill(user_id)
                    elif user_choice == "5":
                        atm.delete_user(user_id)
                        break
                    elif user_choice == "6":
                        break
                    else:
                        print("Invalid choice. Please try again.")
        elif choice == "3":
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
