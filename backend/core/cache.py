import json 
import hashlib 
from functools import wraps 


import redis 
from flask import request, jsonify

from .logger import logger 
import os

try: 
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    redis_client = redis.from_url(redis_url, decode_responses=True)
    redis_client.ping()
    REDIS_AVAILABLE=True
    logger.info("Redis cache initialized successfully.")
except:
    redis_client = None 
    REDIS_AVAILABLE=False
    logger.error("Redis cache initialization failed.")

def cached(prefix:str, ttl:int =30):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not REDIS_AVAILABLE: 
                return func(*args, **kwargs)
            
            raw_key = f"{request.path}:{str(request.args)}"
            key = hashlib.md5(raw_key.encode()).hexdigest()
            key = f"chikitsa:{prefix}:{key}"
            try: 
                cached_data = redis_client.get(key)
                if cached_data: 
                    logger.info(f"Cache hit for key: {prefix}")
                    return jsonify(json.loads(cached_data)), 200 
            except Exception as e:
                logger.error(f"Cache set error: {e}")

            response = func(*args, **kwargs)

            try: 
                if isinstance(response, tuple):
                    data, code = response 
                    if code ==200 and hasattr(data, 'get_json'):
                        redis_client.setex(key, ttl, json.dumps(data.get_json(), default=str))
                        logger.info(f"Cache SET: {prefix}")
                elif hasattr(response, 'get_json'):  
                    redis_client.setex(key, ttl, json.dumps(response.get_json(), default=str))
                    logger.info(f"Cache SET: {prefix}")
            except Exception as e:
                logger.error(f"Cache set error: {e}")
                
            return response 

        return wrapper 

    return decorator 


def invalidate(prefix:str):
    if REDIS_AVAILABLE: 
        try: 
            keys = redis_client.keys(f"chikitsa:{prefix}:*")
            if keys: 
                redis_client.delete(*keys)
                logger.info(f"Cache invalidated for prefix: {prefix}")
        except: 
            pass 
    

