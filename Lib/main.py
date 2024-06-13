from models import BankATM
from colorama import Fore

def main():
    atm = BankATM()
    while True:
        try:
            print(Fore.YELLOW + "\n--- Welcome to Dhabiti_ATM_Banking ---")
            print("1. Create an Account")
            print("2. Login to your Account")
            print("3. Exit")
            choice = input(Fore.CYAN + "Choose an option: ")
            if choice == "1":
                atm.create_user()
            elif choice == "2":
                user_id = atm.login()
                if user_id:
                    while True:
                        print(Fore.YELLOW + "\n--- My Menu ---")
                        print("1. Deposit")
                        print("2. Withdraw")
                        print("3. View Balance")
                        print("4. Pay Bill")
                        print("5. Delete Account")
                        print("6. Logout")
                        user_choice = input(Fore.CYAN + "Choose an option: ")
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
            elif choice == "3":
                print(Fore.GREEN + "Thank you for using Dhabiti_ATM_Banking. Goodbye!")
                break
        except Exception as e:
            print(Fore.RED + f"An error occurred: {e}")

if __name__ == "__main__":
    main()
