"""
simple_accounts.py
────────────────────
"""
class SimpleAccounts:
    def __init__(self):
        self.accounts = [
            {"email": "gemy28500@gmail.com", "password": "Idor_Hunter33"},
            {"email": "k77614005@gmail.com", "password": "Idor_Hunter34"},
            {"email": "Celarens33@gmail.com", "password": "Idor_Hunter35"},
            {"email": "m39060649@gmail.com", "password": "Idor_Hunter36"},
            {"email": "mark5794685@gmail.com", "password": "Idor_Hunter37"}
        ]
    
    def get_count(self):
        return len(self.accounts)
    
    def get_account(self, index):
        if 0 <= index < len(self.accounts):
            return self.accounts[index]
        return None
    
    def list_accounts(self):
        for i, acc in enumerate(self.accounts):
            print(f"{i+1}. {acc['email']}")
