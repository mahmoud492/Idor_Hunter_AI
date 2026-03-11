"""
html_analyzer.py
────────────────────
"""
from bs4 import BeautifulSoup

class HTMLAnalyzer:
    def analyze_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        forms = len(soup.find_all('form'))
        links = len(soup.find_all('a'))
        return {"forms": forms, "links": links}
