REDIS_BUFFER_SIZE = 10

REDIS_EVENT_PROCESSOR_KEY = "analytics_events"

# Consumer groups listening on the analytics_events stream.
# Each group gets an independent cursor — all groups receive every message.
REDIS_EVENT_PROCESSOR_GROUPS = [
    "event_processor_group",
]

REDIS_STREAM_MAPPING = {
    REDIS_EVENT_PROCESSOR_KEY: REDIS_EVENT_PROCESSOR_GROUPS,
}
