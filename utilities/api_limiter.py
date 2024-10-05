from fastapi import Request, HTTPException
from utilities.utils import rds_dependency


class ApiLimitDependency:
    def __init__(self, req_per_5_sec):
        self.req_per_5_sec = req_per_5_sec

    def __call__(self, request: Request, rds: rds_dependency):
        client_ip = request.client.host
        base_url = request.url
        rds_parameter = str(client_ip) + str(base_url)
        cache = rds.get(rds_parameter)
        print("REQUEST PARAMETER : ", rds_parameter)
        print("REQUEST CACHE :", cache)
        if cache:
            cache = int(cache)
            if cache <= 0:
                raise HTTPException(status_code=429, detail="too many requests")
            
            cache -= 1
            ttl = rds.ttl(rds_parameter)
            rds.setex(rds_parameter, ttl, cache)
            
        else:
            rds.setex(rds_parameter, 5, int(self.req_per_5_sec))
            
        return None