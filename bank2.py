import json
import datetime



class InsufficientFundsError(Exception):
    pass


class InvalidAmountError(Exception):
    pass



class Transaction:
    def __init__(self, t_type, amount):
        self.type = t_type
        self.amount = amount
        self.time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def __str__(self):
        return f"{self.time} - {self.type}: {self.amount}"



class Account:
    def __init__(self, account_id):
        self.account_id = account_id
        self._balance = 0
        self.transactions = []

    def deposit(self, amount):
        if amount <= 0:
            raise InvalidAmountError("Invalid amount")
        self._balance += amount
        self.transactions.append(Transaction("deposit", amount))

    def withdraw(self, amount):
        if amount <= 0:
            raise InvalidAmountError("Invalid amount")
        if amount > self._balance:
            raise InsufficientFundsError("Not enough balance")
        self._balance -= amount
        self.transactions.append(Transaction("withdraw", amount))

    def get_balance(self):
        return self._balance

    def show_transactions(self):
        for t in self.transactions:
            print(t)



class SavingsAccount(Account):
    def withdraw(self, amount):
        if amount > 1000:
            raise Exception("Max withdraw is 1000")
        super().withdraw(amount)



class CheckingAccount(Account):
    def withdraw(self, amount):
        fee = 2
        total = amount + fee
        if total > self._balance:
            raise InsufficientFundsError("Not enough balance")
        self._balance -= total
        self.transactions.append(Transaction("withdraw + fee", total))



class User:
    def __init__(self, name):
        self.name = name
        self.accounts = {}

    def add_account(self, account):
        self.accounts[account.account_id] = account



class Bank:
    def __init__(self):
        self.users = {}

    def add_user(self, name):
        self.users[name] = User(name)

    def create_account(self, username, acc_type, acc_id):
        if acc_type == "savings":
            acc = SavingsAccount(acc_id)
        elif acc_type == "checking":
            acc = CheckingAccount(acc_id)
        else:
            print("Invalid type")
            return

        self.users[username].add_account(acc)

    def transfer(self, u1, a1, u2, a2, amount):
        from_acc = self.users[u1].accounts[a1]
        to_acc = self.users[u2].accounts[a2]

        from_acc.withdraw(amount)
        to_acc.deposit(amount)

    def save(self):
        data = {}
        for uname, user in self.users.items():
            data[uname] = {}
            for acc_id, acc in user.accounts.items():
                data[uname][acc_id] = acc.get_balance()

        with open("bank.json", "w") as f:
            json.dump(data, f)

    def load(self):
        try:
            with open("bank.json", "r") as f:
                data = json.load(f)

            for uname in data:
                self.add_user(uname)
                for acc_id, balance in data[uname].items():
                    acc = Account(acc_id)
                    acc._balance = balance
                    self.users[uname].add_account(acc)
        except:
            pass