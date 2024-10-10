from fastapi import Request, HTTPException
from utilities.utils import rds_dependency


class ApiLimitDependency:
    def __init__(self, req_count, time_frame_in_sec=5):
        self.req_count = req_count
        self.time_frame_in_sec = time_frame_in_sec

    def __call__(self, request: Request, rds: rds_dependency):
        client_ip = request.client.host
        base_url = request.url
        rds_parameter = str(client_ip) + str(base_url)
        cache = rds.get(rds_parameter)
        if cache:
            cache = int(cache)
            if cache <= 0:
                raise HTTPException(status_code=429, detail="too many requests")

            cache -= 1
            ttl = rds.ttl(rds_parameter)
            rds.setex(rds_parameter, ttl, cache)

        else:
            rds.setex(rds_parameter, self.time_frame_in_sec, int(self.req_count))

        return None
