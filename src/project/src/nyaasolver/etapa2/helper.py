def is_full_time_worker(worker, demand_workers):
    """Check if a worker is full time."""
    try:
        demand_workers["TC"].index(worker)
        return True
    except:
        return False