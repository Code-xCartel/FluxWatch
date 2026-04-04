import os
import random
import argparse
import asyncio
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")


# MUST match your backend exactly
EVENT_TYPES: dict[str, list[str]] = {
    "user": ["user.login", "user.logout"],
    "order": ["order.created", "order.completed", "order.cancelled"],
    "system": ["system.metric"],
    "session": ["session.started", "session.ended"],
}

PRODUCERS = ["webapp", "mobile", "edge-agent", "scheduler", "admin-panel"]
SOURCES = ["web", "mobile", "system"]


def random_entity() -> dict[str, str]:
    """EventEntity: type (Literal["user","order","system","session"]), id (str)"""
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


def random_actor() -> dict[str, str | None] | None:
    """EventActor: type (str | None), id (str | None)"""
    if random.random() < 0.30:
        return None

    if random.random() < 0.6:
        return {"type": "user", "id": f"user_{random.randint(1, 2000)}"}

    return {"type": "service", "id": random.choice(["auth", "billing", "analytics", "rust-engine"])}


def make_context(entity: dict[str, str]) -> dict[str, str | None]:
    """EventContext: trace_id (str | None), session_id (str | None), source (str | None)"""
    session_id = entity["id"] if entity["type"] == "session" else f"session_{uuid4()}"

    return {
        "traceId": str(uuid4()),
        "sessionId": session_id,
        "source": random.choice(SOURCES),
    }


def make_payload(event_type: str) -> dict[str, Any]:
    """payload: dict[str, Any] — free-form event data"""
    base: dict[str, Any] = {
        "ip": ".".join(str(random.randint(1, 255)) for _ in range(4)),
        "device": random.choice(["ios", "android", "web"]),
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
            ),
        }

    elif event_type == "session.started":
        base |= {"session_kind": "authenticated"}

    elif event_type == "session.ended":
        base |= {
            "duration_sec": random.randint(5, 7200),
            "ended_by": random.choice(["user", "timeout", "server"]),
        }

    elif event_type == "system.metric":
        base |= {
            "cpu": round(random.uniform(1, 99), 2),
            "memory": round(random.uniform(5, 98), 2),
            "disk": round(random.uniform(10, 95), 2),
            "latency_ms": random.randint(5, 3000),
        }

    return base


def generate_event() -> dict[str, Any]:
    """Builds an Event-shaped dict matching the API model (camelCase keys)."""
    entity = random_entity()
    entity_type = entity["type"]
    event_type = random.choice(EVENT_TYPES[entity_type])

    return {
        "entity": entity,
        "eventType": event_type,
        "producer": random.choice(PRODUCERS),
        "occurredAt": datetime.now(timezone.utc).isoformat(),
        "actor": random_actor(),
        "context": make_context(entity),
        "payload": make_payload(event_type),
    }


async def send_one(client: httpx.AsyncClient, url: str, event: dict, headers: dict) -> tuple[bool, int, str]:
    try:
        r = await client.post(url, json=event, headers=headers)
        if 200 <= r.status_code < 300:
            return True, r.status_code, ""
        return False, r.status_code, r.text[:250]
    except Exception as e:
        return False, 0, str(e)


async def run_bursts(
    url: str,
    api_token: str,
    total: int,
    batch_size: int,
    concurrency: int,
    timeout: float,
):
    limits = httpx.Limits(
        max_connections=max(100, concurrency * 2),
        max_keepalive_connections=max(50, concurrency),
    )
    client_timeout = httpx.Timeout(timeout)

    sem = asyncio.Semaphore(concurrency)

    headers = {"Authorization": f"ApiKey {api_token}"} if api_token else {}

    sent = 0
    ok = 0
    failed = 0

    async with httpx.AsyncClient(timeout=client_timeout, limits=limits) as client:

        async def guarded_send(ev: dict):
            async with sem:
                return await send_one(client, url, ev, headers)

        while sent < total:
            current_batch = min(batch_size, total - sent)
            events = [generate_event() for _ in range(current_batch)]

            tasks = [asyncio.create_task(guarded_send(e)) for e in events]
            results = await asyncio.gather(*tasks)

            batch_errors = []
            for success, status, err in results:
                sent += 1
                if success:
                    ok += 1
                else:
                    failed += 1
                    batch_errors.append(f"status={status} err={err}")

            print(
                f"progress: sent={sent}/{total} ok={ok} failed={failed} "
                f"(batch={current_batch}, concurrency={concurrency})"
            )
            for e in batch_errors:
                print(f"  [FAIL] {e}")

    print("\n--- final summary ---")
    print(f"total:  {total}")
    print(f"ok:     {ok}")
    print(f"failed: {failed}")


def main():
    parser = argparse.ArgumentParser(description="Burst event generator (matches EventCreate + your EVENT_TYPES)")
    parser.add_argument("--total", type=int, default=5000, help="Total events to send")
    parser.add_argument("--batch-size", type=int, default=250, help="Events per batch")
    parser.add_argument("--concurrency", type=int, default=50, help="Max in-flight requests")
    parser.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout seconds")
    args = parser.parse_args()

    url = os.getenv("EVENT_API_URL", "http://localhost:8000/events/ingest")
    api_token = os.getenv("API_TOKEN", "")

    print(f"POST -> {url}")
    print(
        f"total={args.total}, batch_size={args.batch_size}, "
        f"concurrency={args.concurrency}, timeout={args.timeout}s\n"
    )

    asyncio.run(
        run_bursts(
            url=url,
            api_token=api_token,
            total=args.total,
            batch_size=args.batch_size,
            concurrency=args.concurrency,
            timeout=args.timeout,
        )
    )


if __name__ == "__main__":
    main()
