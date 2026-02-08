import os
import random
import argparse
import asyncio
from uuid import uuid4
from datetime import datetime, timezone
from typing import Any

import httpx


# MUST match your backend exactly
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
    # 30% no actor
    if random.random() < 0.30:
        return None

    actor_type = random.choice(ACTOR_TYPES)

    if actor_type == "user":
        return {"type": "user", "id": f"user_{random.randint(1, 2000)}"}

    return {"type": "service", "id": random.choice(["auth", "billing", "analytics", "rust-engine"])}


def make_context(entity: dict[str, str]) -> dict[str, Any]:
    # Your API currently requires these (even if the model says Optional)
    session_id = entity["id"] if entity["type"] == "session" else f"session_{uuid4()}"

    return {
        "trace_id": str(uuid4()),
        "session_id": session_id,
        "source": random.choice(SOURCES),

        # extra metadata
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

    # USER
    if event_type == "user.login":
        base |= {
            "method": random.choice(["password", "google", "github"]),
            "success": random.choice([True, True, True, False]),
            "geo": random.choice(["US", "IN", "DE", "BR", "GB"]),
        }

    elif event_type == "user.logout":
        base |= {"reason": random.choice(["user_action", "timeout", "forced"])}

    # ORDER
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

    # SESSION
    elif event_type == "session.started":
        base |= {"device": random.choice(["ios", "android", "web"]), "session_kind": "authenticated"}

    elif event_type == "session.ended":
        base |= {
            "duration_sec": random.randint(5, 7200),
            "ended_by": random.choice(["user", "timeout", "server"]),
        }

    # SYSTEM
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

    event = {
        "entity": entity,
        "event_type": event_type,
        "producer": random.choice(PRODUCERS),
        "actor": random_actor(),
        "context": make_context(entity),
        "payload": make_payload(event_type),
    }

    # your model allows these as None, but don't null context (API wants it)
    if random.random() < 0.10:
        event["actor"] = None

    # sometimes payload empty
    if random.random() < 0.03:
        event["payload"] = {}

    return event


async def send_one(client: httpx.AsyncClient, url: str, event: dict) -> tuple[bool, int, str]:
    try:
        r = await client.post(url, json=event)
        if 200 <= r.status_code < 300:
            return True, r.status_code, ""
        return False, r.status_code, r.text[:250]
    except Exception as e:
        return False, 0, str(e)


async def run_bursts(
    url: str,
    total: int,
    batch_size: int,
    concurrency: int,
    timeout: float,
    pretty_fail: bool,
):
    limits = httpx.Limits(
        max_connections=max(100, concurrency * 2),
        max_keepalive_connections=max(50, concurrency),
    )
    client_timeout = httpx.Timeout(timeout)

    sem = asyncio.Semaphore(concurrency)

    sent = 0
    ok = 0
    failed = 0

    async with httpx.AsyncClient(timeout=client_timeout, limits=limits) as client:

        async def guarded_send(ev: dict):
            async with sem:
                return await send_one(client, url, ev)

        while sent < total:
            current_batch = min(batch_size, total - sent)
            events = [generate_event() for _ in range(current_batch)]

            tasks = [asyncio.create_task(guarded_send(e)) for e in events]
            results = await asyncio.gather(*tasks)

            for success, status, err in results:
                sent += 1
                if success:
                    ok += 1
                else:
                    failed += 1
                    if pretty_fail:
                        print(f"[FAIL] status={status} err={err}")

            print(
                f"progress: sent={sent}/{total} ok={ok} failed={failed} "
                f"(batch={current_batch}, concurrency={concurrency})"
            )

    print("\n--- final summary ---")
    print(f"total:  {total}")
    print(f"ok:     {ok}")
    print(f"failed: {failed}")


def main():
    parser = argparse.ArgumentParser(description="Burst event generator (matches EventCreate + your EVENT_TYPES)")
    parser.add_argument(
        "--url",
        default=os.getenv("EVENT_API_URL", "http://localhost:8000/events"),
        help="Ingestion endpoint URL (or set EVENT_API_URL)",
    )
    parser.add_argument("--total", type=int, default=5000, help="Total events to send")
    parser.add_argument("--batch-size", type=int, default=250, help="Events per batch")
    parser.add_argument("--concurrency", type=int, default=50, help="Max in-flight requests")
    parser.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout seconds")
    parser.add_argument("--pretty-fail", action="store_true", help="Print failures in detail")
    args = parser.parse_args()

    print(f"POST -> {args.url}")
    print(
        f"total={args.total}, batch_size={args.batch_size}, "
        f"concurrency={args.concurrency}, timeout={args.timeout}s\n"
    )

    asyncio.run(
        run_bursts(
            url=args.url,
            total=args.total,
            batch_size=args.batch_size,
            concurrency=args.concurrency,
            timeout=args.timeout,
            pretty_fail=args.pretty_fail,
        )
    )


if __name__ == "__main__":
    main()
