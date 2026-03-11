"""
api_detector.py
────────────────────
"""
import re

class APIDetector:
    def detect_from_text(self, text):
        endpoints = re.findall(r'/api/[a-zA-Z0-9_\-/]+', text)
        return {"endpoints": list(set(endpoints))}
