import logging

import redis

logger = logging.getLogger(__name__)


class Redis:
    def __init__(self, redis_url):
        try:
            logger.info("Connecting to Redis DB")
            self.client = redis.Redis.from_url(url=redis_url)
            if self.client.ping():
                logger.info("Connected to Redis DB successfully.")
        except redis.exceptions.ConnectionError:
            logger.error("Unable to connect to Redis server.")
