"""
add_target.py
────────────────────
"""
import os

TARGETS_FILE = "targets.txt"

def add_target(url):
    with open(TARGETS_FILE, 'a') as f:
        f.write(url + "\n")
    print(f"✅ Added: {url}")

def show_targets():
    if os.path.exists(TARGETS_FILE):
        with open(TARGETS_FILE, 'r') as f:
            targets = f.readlines()
        for i, t in enumerate(targets):
            print(f"{i+1}. {t.strip()}")
    else:
        print("No targets yet")

if __name__ == "__main__":
    show_targets()
