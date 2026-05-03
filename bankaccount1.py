import json
import uuid
from abc import ABC, abstractmethod
from datetime import datetime



class BankingError(Exception): pass


class InsufficientFundsError(BankingError): pass


class InvalidAmountError(BankingError): pass




class Transaction:
    def __init__(self, t_type, amount, balance_after):
        self.t_type = t_type
        self.amount = amount
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.balance_after = balance_after

    def to_dict(self):
        return self.__dict__


class Account(ABC):
    def __init__(self, account_id, initial_balance=0):
        self.account_id = account_id
        self._balance = initial_balance  # Encapsulation
        self.history = []

    @property
    def balance(self):
        return self._balance

    def deposit(self, amount):
        if amount <= 0:
            raise InvalidAmountError("Deposit must be positive.")
        self._balance += amount
        self._record_transaction("Deposit", amount)
        return self._balance

    @abstractmethod
    def withdraw(self, amount):
        pass

    def _record_transaction(self, t_type, amount):
        tx = Transaction(t_type, amount, self._balance)
        self.history.append(tx)

    def to_dict(self):
        return {
            "type": self.__class__.__name__,
            "id": self.account_id,
            "balance": self._balance,
            "history": [t.to_dict() for t in self.history]
        }


class SavingsAccount(Account):
    def __init__(self, account_id, balance=0, interest_rate=0.02):
        super().__init__(account_id, balance)
        self.interest_rate = interest_rate

    def withdraw(self, amount):
        if amount > self._balance:
            raise InsufficientFundsError("Savings accounts cannot be overdrawn.")
        self._balance -= amount
        self._record_transaction("Withdrawal", amount)

    def apply_interest(self):
        interest = self._balance * self.interest_rate
        self._balance += interest
        self._record_transaction("Interest Applied", interest)


class CheckingAccount(Account):
    def __init__(self, account_id, balance=0, overdraft_limit=500):
        super().__init__(account_id, balance)
        self.overdraft_limit = overdraft_limit

    def withdraw(self, amount):
        if amount > (self._balance + self.overdraft_limit):
            raise InsufficientFundsError("Exceeds overdraft limit.")
        self._balance -= amount
        self._record_transaction("Withdrawal", amount)


class User:
    def __init__(self, username, pin):
        self.username = username
        self.pin = pin
        self.accounts = {}

    def add_account(self, account):
        self.accounts[account.account_id] = account


class Bank:
    def __init__(self, storage_file="bank_data.json"):
        self.users = {}
        self.storage_file = storage_file
        self.load_data()

    def create_user(self, username, pin):
        if username in self.users:
            return False
        self.users[username] = User(username, pin)
        return True

    def authenticate(self, username, pin):
        user = self.users.get(username)
        if user and user.pin == pin:
            return user
        return None

    def transfer(self, from_acc, to_acc, amount):
        from_acc.withdraw(amount)
        to_acc.deposit(amount)

    def save_data(self):
        data = {}
        for uname, user in self.users.items():
            data[uname] = {
                "pin": user.pin,
                "accounts": [acc.to_dict() for acc in user.accounts.values()]
            }
        with open(self.storage_file, 'w') as f:
            json.dump(data, f)

    def load_data(self):
        try:
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                for uname, udata in data.items():
                    user = User(uname, udata["pin"])
                    for acc_data in udata["accounts"]:
                        if acc_data["type"] == "SavingsAccount":
                            acc = SavingsAccount(acc_data["id"], acc_data["balance"])
                        else:
                            acc = CheckingAccount(acc_data["id"], acc_data["balance"])
                        user.add_account(acc)
                    self.users[uname] = user
        except FileNotFoundError:
            pass



def main():
    bank = Bank()
    print("Welcome to Pythonic Bank")

    while True:
        choice = input("\n1. Register\n2. Login\n3. Exit\nSelection: ")

        if choice == '1':
            user = input("Username: ")
            pin = input("PIN: ")
            if bank.create_user(user, pin):
                print("Registration successful!")
            else:
                print("Username taken.")

        elif choice == '2':
            user_obj = bank.authenticate(input("Username: "), input("PIN: "))
            if user_obj:
                user_menu(bank, user_obj)
            else:
                print("Invalid credentials.")

        elif choice == '3':
            bank.save_data()
            break


def user_menu(bank, user):
    while True:
        print(f"\n--- Hello, {user.username} ---")
        print("1. Open Account\n2. Deposit\n3. Withdraw\n4. View History\n5. Logout")
        choice = input("Selection: ")

        try:
            if choice == '1':
                acc_type = input("S for Savings, C for Checking: ").upper()
                acc_id = str(uuid.uuid4())[:8]
                if acc_type == 'S':
                    user.add_account(SavingsAccount(acc_id))
                else:
                    user.add_account(CheckingAccount(acc_id))
                print(f"Account {acc_id} opened.")

            elif choice == '2':
                acc_id = input("Account ID: ")
                amt = float(input("Amount: "))
                user.accounts[acc_id].deposit(amt)
                print("Success.")

            elif choice == '3':
                acc_id = input("Account ID: ")
                amt = float(input("Amount: "))
                user.accounts[acc_id].withdraw(amt)
                print("Success.")

            elif choice == '4':
                for acc in user.accounts.values():
                    print(f"\nAccount {acc.account_id} | Balance: {acc.balance}")
                    for tx in acc.history:
                        print(f"  {tx.timestamp} - {tx.t_type}: ${tx.amount}")

            elif choice == '5':
                break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    main()