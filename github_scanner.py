"""
github_scanner.py
────────────────────
"""
import os
import github3

class GitHubScanner:
    def __init__(self):
        self.gh = github3.login(token=os.getenv("GITHUB_TOKEN"))
