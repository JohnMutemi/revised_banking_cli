from models import BankATM
from colorama import Fore

def main():
    # Instantiate the BankATM class to initialize the ATM system
    atm = BankATM()

    while True:
        try:
            # Display the main menu
            print(Fore.YELLOW + "\n--- Welcome to Dhabiti_ATM_Banking ---")
            print("1. Create an Account")
            print("2. Login to your Account")
            print("3. Exit")
            
            # Get user input for the main menu choice
            choice = input(Fore.CYAN + "Choose an option: ")
            
            # Handle user choice
            if choice == "1":
                atm.create_user()  # Call create_user method to register a new user
            elif choice == "2":
                user_id = atm.login()  # Call login method to authenticate user
                
                if user_id:
                    # Authenticated user's menu
                    while True:
                        print(Fore.YELLOW + "\n--- My Menu ---")
                        print("1. Deposit")
                        print("2. Withdraw")
                        print("3. View Balance")
                        print("4. Pay Bill")
                        print("5. View Transactions")  
                        print("6. Delete Account")
                        print("7. Logout")
                        
                        # Get user input for the authenticated user's menu choice
                        user_choice = input(Fore.CYAN + "Choose an option: ")
                        
                        # Handle user choice
                        if user_choice == "1":
                            atm.deposit(user_id)  # Call deposit method
                        elif user_choice == "2":
                            atm.withdraw(user_id)  # Call withdraw method
                        elif user_choice == "3":
                            atm.view_balance(user_id)  # Call view_balance method
                        elif user_choice == "4":
                            atm.pay_bill(user_id)  # Call pay_bill method
                        elif user_choice == "5":
                            atm.view_transactions(user_id)  # Call view_transactions method
                        elif user_choice == "6":
                            atm.delete_user(user_id)  # Call delete_user method
                            break  # Exit to main menu after deleting the account
                        elif user_choice == "7":
                            break  # Logout and return to main menu
            elif choice == "3":
                # Exit the application
                print(Fore.GREEN + "Thank you for using Dhabiti_ATM_Banking. Goodbye!")
                break  # Exit the while loop to end the program
        except Exception as e:
            # Handle any unexpected errors
            print(Fore.RED + f"An error occurred: {e}")

if __name__ == "__main__":
    main()  # Call the main function to start the application
