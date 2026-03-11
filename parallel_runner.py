"""
parallel_runner.py
────────────────────
"""
from concurrent.futures import ThreadPoolExecutor

class ParallelRunner:
    def __init__(self, max_workers=5):
        self.pool = ThreadPoolExecutor(max_workers=max_workers)
    
    def run_tasks(self, tasks, args_list):
        futures = [self.pool.submit(t, *a) for t, a in zip(tasks, args_list)]
        return [f.result() for f in futures]
