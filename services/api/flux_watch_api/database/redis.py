import logging

import redis

from flux_watch_api.utils.constants import REDIS_BUFFER_SIZE, REDIS_STREAM_MAPPING

logger = logging.getLogger(__name__)


class Redis:
    def __init__(self, redis_url):
        try:
            logger.info("Connecting to Redis DB")
            self.client = redis.Redis.from_url(url=redis_url)
            if self.client.ping():
                logger.info("Connected to Redis DB successfully.")
                self._ensure_consumer_groups()
        except redis.exceptions.ConnectionError:
            logger.error("Unable to connect to Redis server.")

        self._buffer: list[tuple[str, dict]] = []

    def _ensure_consumer_groups(self):
        """Create all consumer groups on the stream if they don't already exist.
        Each group gets an independent cursor — adding a new group here means it
        will receive all future messages without any changes to the producer side.
        """
        for stream in REDIS_STREAM_MAPPING:
            for group in REDIS_STREAM_MAPPING[stream]:
                try:
                    # MKSTREAM creates the stream if it doesn't exist yet
                    # "$" means the group only receives messages added after creation
                    self.client.xgroup_create(stream, group, id="$", mkstream=True)
                    logger.info(f"Created consumer group '{group}' on stream '{stream}'")
                except redis.exceptions.ResponseError as e:
                    if "BUSYGROUP" in str(e):
                        logger.info(f"Consumer group '{group}' already exists, skipping.")
                    else:
                        raise

    def publish(self, stream: str, fields: dict) -> None:
        """Buffer a message and flush to the stream once the buffer is full."""
        self._buffer.append((stream, fields))
        if len(self._buffer) >= REDIS_BUFFER_SIZE:
            self.flush()

    def flush(self) -> None:
        if not self._buffer:
            return
        pipe = self.client.pipeline()
        for stream, fields in self._buffer:
            pipe.xadd(stream, fields)
        pipe.execute()
        self._buffer.clear()

    def xadd(self, stream: str, fields: dict, maxlen: int | None = None) -> str:
        """Add a single message to a stream immediately. Returns the generated message ID."""
        return self.client.xadd(stream, fields, maxlen=maxlen, approximate=True)
