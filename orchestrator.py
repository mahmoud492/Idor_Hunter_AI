"""
orchestrator.py
────────────────────
"""
from parallel_runner import ParallelRunner

class IDOROrchestrator:
    def __init__(self):
        self.runner = ParallelRunner()
        self.agents = {}
    
    def analyze_target(self, url):
        return {"target": url, "status": "analyzed"}
