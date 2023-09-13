import time
from pxr import Sdf,Usd,UsdUtils



def wait_for_stage(timeout=10) -> Usd.Stage:
    end_time = time.time() + timeout
    while time.time() < end_time:
        stages = UsdUtils.StageCache.Get().GetAllStages()
        if stages:
            return stages[0]
        time.sleep(0.1)  # Sleep for 100 milliseconds before checking again
    return None