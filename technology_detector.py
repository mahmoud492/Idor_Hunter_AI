"""
technology_detector.py
────────────────────
"""
class TechnologyDetector:
    def detect_from_headers(self, headers):
        server = headers.get('Server', 'Unknown')
        return {"server": server}
