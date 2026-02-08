import os
import json
import random
import argparse
from uuid import uuid4
from datetime import datetime, timezone
from typing import Any

import httpx


EVENT_TYPES: dict[str, list[str]] = {
    "user": ["user.login", "user.logout"],
    "order": ["order.created", "order.completed", "order.cancelled"],
    "system": ["system.metric"],
    "session": ["session.started", "session.ended"],
}

PRODUCERS = ["webapp", "mobile", "edge-agent", "scheduler", "admin-panel"]
ACTOR_TYPES = ["user", "service"]
SOURCES = ["web", "mobile", "system", "backend", "edge-agent"]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def random_entity() -> dict[str, str]:
    entity_type = random.choice(list(EVENT_TYPES.keys()))

    if entity_type == "user":
        entity_id = f"user_{random.randint(1, 2000)}"
    elif entity_type == "order":
        entity_id = f"order_{random.randint(10000, 999999)}"
    elif entity_type == "session":
        entity_id = f"session_{uuid4()}"
    else:
        entity_id = f"system_{random.randint(1, 50)}"

    return {"type": entity_type, "id": entity_id}


def random_actor() -> dict[str, str] | None:
    if random.random() < 0.30:
        return None

    actor_type = random.choice(ACTOR_TYPES)

    if actor_type == "user":
        return {"type": "user", "id": f"user_{random.randint(1, 2000)}"}

    return {"type": "service", "id": random.choice(["auth", "billing", "analytics", "rust-engine"])}


def make_context(entity: dict[str, str]) -> dict[str, Any]:
    # Always send these 3 because your API currently requires them
    session_id = entity["id"] if entity["type"] == "session" else f"session_{uuid4()}"

    return {
        "trace_id": str(uuid4()),
        "session_id": session_id,
        "source": random.choice(SOURCES),

        # extra metadata (safe to include)
        "ip": ".".join(str(random.randint(1, 255)) for _ in range(4)),
        "user_agent": random.choice(
            ["Mozilla/5.0", "curl/8.0.1", "PostmanRuntime/7.36.0", "python-httpx/0.x"]
        ),
        "env": random.choice(["dev", "staging", "prod"]),
        "tags": random.sample(
            ["payments", "security", "ops", "billing", "auth"],
            k=random.randint(1, 3),
        ),
        "ts": utc_now_iso(),
    }


def make_payload(event_type: str) -> dict[str, Any]:
    base: dict[str, Any] = {
        "request_id": str(uuid4()),
    }

    if event_type == "user.login":
        base |= {
            "method": random.choice(["password", "google", "github"]),
            "success": random.choice([True, True, True, False]),
            "geo": random.choice(["US", "IN", "DE", "BR", "GB"]),
        }

    elif event_type == "user.logout":
        base |= {"reason": random.choice(["user_action", "timeout", "forced"])}

    elif event_type == "order.created":
        base |= {
            "amount": round(random.uniform(5, 500), 2),
            "currency": random.choice(["USD", "EUR", "GBP", "INR"]),
            "items": random.randint(1, 6),
        }

    elif event_type == "order.completed":
        base |= {
            "paid": True,
            "payment_provider": random.choice(["stripe", "paypal", "razorpay"]),
            "receipt_id": f"rcpt_{uuid4().hex[:12]}",
        }

    elif event_type == "order.cancelled":
        base |= {
            "cancel_reason": random.choice(
                ["user_request", "payment_failed", "out_of_stock", "fraud_detected"]
            )
        }

    elif event_type == "session.started":
        base |= {"device": random.choice(["ios", "android", "web"]), "session_kind": "authenticated"}

    elif event_type == "session.ended":
        base |= {"duration_sec": random.randint(5, 7200), "ended_by": random.choice(["user", "timeout", "server"])}

    elif event_type == "system.metric":
        base |= {
            "cpu": round(random.uniform(1, 99), 2),
            "memory": round(random.uniform(5, 98), 2),
            "disk": round(random.uniform(10, 95), 2),
            "latency_ms": random.randint(5, 3000),
        }

    return base


def generate_event() -> dict[str, Any]:
    entity = random_entity()
    entity_type = entity["type"]
    event_type = random.choice(EVENT_TYPES[entity_type])

    return {
        "entity": entity,
        "event_type": event_type,
        "producer": random.choice(PRODUCERS),
        "actor": random_actor(),
        "context": make_context(entity),  # fixed
        "payload": make_payload(event_type),
    }


def main():
    parser = argparse.ArgumentParser(description="Send a single valid EventCreate payload")
    parser.add_argument(
        "--url",
        default=os.getenv("EVENT_API_URL", "http://localhost:8000/events"),
        help="Ingestion endpoint URL (or set EVENT_API_URL)",
    )
    parser.add_argument("--print", action="store_true", help="Print JSON payload")
    parser.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout seconds")
    args = parser.parse_args()

    event = generate_event()

    if args.print:
        print(json.dumps(event, indent=2))

    with httpx.Client(timeout=args.timeout) as client:
        r = client.post(args.url, json=event)

    print(f"status: {r.status_code}")
    try:
        print("response:", r.json())
    except Exception:
        print("response:", r.text[:800])


if __name__ == "__main__":
    main()
