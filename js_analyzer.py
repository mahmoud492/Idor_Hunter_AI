"""
js_analyzer.py
────────────────────
"""
import re
import json

class JSAnalyzer:
    def analyze_js(self, js_content):
        endpoints = re.findall(r'["\'](/api/[^"\']*)["\']', js_content)
        return {"endpoints": list(set(endpoints))}
