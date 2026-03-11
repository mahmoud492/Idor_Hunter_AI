"""
priority_ranker.py
────────────────────
"""
class PriorityRanker:
    def rank_vulnerabilities(self, vulns):
        return sorted(vulns, key=lambda x: x.get('score', 0), reverse=True)
