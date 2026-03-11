"""
pattern_matcher.py
────────────────────
"""
import re

class PatternMatcher:
    def extract_ids(self, text):
        numeric = re.findall(r'\b\d{4,}\b', text)
        return {"numeric": numeric}
