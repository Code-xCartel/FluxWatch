# FluxWatch Analytics Engine Documentation

---

## Overview

The Analytics Engine is a real-time event processing system designed to detect and escalate error spikes in system metrics. It processes incoming events, applies configurable rules, and generates alerts with severity levels based on defined thresholds.

> Core Purpose: Detect error patterns, escalate appropriately, and prevent notification fatigue through intelligent state management.

---

# Project Goals

| # | Goal |
|---|------|
| 1 | Detect error spikes in real-time system metrics with minimal latency |
| 2 | Provide intelligent alert escalation based on configurable severity thresholds |
| 3 | Prevent alert spam through state management and sustained error tracking |
| 4 | Track event correlation with unique identifiers for debugging and analysis |
| 5 | Build a scalable foundation for multiple rule types and event processors |
| 6 | Maintain clean separation of concerns through modular architecture |

---

# Architecture Components

## 1. Events Module

**Responsibility:** Represent incoming system events

**Key Types:**
- `EventType` - Types of events (currently: SystemMetrics)
- `Event` - Event data with ID, type, and timestamp

**How it works:**
- External events are polled
- Each event gets a unique UUID
- Events are routed based on their type

---

## 2. Rules Module

**Responsibility:** Implement detection logic and alert generation

**Key Types:**
- `EventRule` - Trait defining the rule interface
- `RuleEngine` - Routes events to applicable rules
- `ErrorSpikeRule` - Detects error spike patterns

**Capabilities:**
- Process events independently
- Maintain sliding time window state
- Generate alerts when conditions met
- Prevent duplicate alerts

---

## 3. Alerts Module

**Responsibility:** Define alert structure and severity

**Alert Levels:**
- High
- Critical
- Severe

**Alert Contains:**
- Type of alert
- Severity level
- Human-readable message
- Timestamp (UTC nanosecond precision)
- Event IDs for traceability

---

## 4. Main Loop

**Responsibility:** Orchestrate event processing

**Cycle:**
1. Poll for new event (1-second interval)
2. Route to RuleEngine
3. Execute applicable rules
4. Output alerts to console
5. Loop indefinitely

---

# Error Spike Rule Behavior

## Configuration

| Setting | Value |
|---------|-------|
| Window Duration | 120 seconds |
| High Threshold | 10 errors |
| Critical Threshold | 25 errors |
| Severe Threshold | 50 errors |

---

## Alert Progression

### Stage 1: INITIAL

**When:** First time error count crosses a threshold

**Example Output:**
```
[INITIAL] 10 errors in last 5s
```

**Note:** Shows actual time span, not full window

---

### Stage 2: ESCALATION

**When:** Alert level increases (High → Critical → Severe)

**Example Output:**
```
[ESCALATION] 25 errors in last 45s
```

**Note:** Only on upward progression

---

### Stage 3: SUSTAINED

**When:** 120 seconds passed AND error count changed

**Example Output:**
```
[SUSTAINED] 50 errors in last 120s
```

**Note:** Prevents spam - only triggers on count change

---

## State Tracking

The rule tracks four pieces of state:

| Field | Purpose |
|-------|---------|
| `events` | Vector of error times (auto-pruned) |
| `last_alert_level` | Current severity level |
| `last_alert_time` | When last alert was sent |
| `last_sustained_count` | Error count at last sustained alert |

---

## State Reset

When error count drops below 10:
- All state is cleared
- Returns to idle mode
- Next spike starts fresh alert cycle

---

## Sliding Window Mechanics

The 2-minute window works by:

1. Adding each new error to the events list
2. Removing errors older than (now - 120 seconds)
3. Current count = errors remaining in window
4. Time span = newest event time - oldest event time

Result: Thresholds always based on recent activity

---

# Implementation Details

## Processing

- Single-threaded synchronous
- 1-second polling
- Immediate alert output
- Blocking I/O (suitable for single deployment)

## Memory

- Auto-pruning keeps memory constant
- Bounded by window duration
- No external allocations needed

## Timestamps

- UTC with nanosecond precision
- Deterministic ordering
- Enables accurate correlation

## Alert Correlation

- Each alert includes event_ids
- Reconstruct error sequences
- Support debugging workflows

---

# Usage Example

```rust
let mut rule_engine = RuleEngine::new();

if let Some(event) = poll_event() {
    if let Some(rule) = rule_engine.rule_for(&event.event_type) {
        if let Some(alert) = rule.process(event) {
            println!("{:?}", alert);
        }
    }
}
```

---

# Current Status

## Completed

- Event ingestion and routing
- Three-tier error spike detection
- Intelligent alert escalation
- Sustained error tracking without spam
- Event correlation and traceability
- State management and reset logic
- Actual timespan calculation

---

# Next Steps: Phase 1

## Monitoring and Metrics (Priority 1)

### What to build:

- [ ] Logging framework for rule processing
- [ ] Metrics collection (alerts generated, events processed)
- [ ] Performance profiling for latency
- [ ] Health check endpoints

### Expected Outcome:

Real-time visibility into engine performance and behavior

---

# Next Steps: Phase 2

## Rule Expansion (Priority 1)

### What to build:

- [ ] Error rate degradation detection
- [ ] Recovery/resolution alerts
- [ ] Configurable rule parameters
- [ ] Multiple spike rules with different thresholds

### Expected Outcome:

More sophisticated detection patterns and flexible configuration

---

# Next Steps: Phase 3

## External Integration (Priority 2)

### What to build:

- [ ] Message queue systems (RabbitMQ, Kafka)
- [ ] HTTP API for event submission
- [ ] Webhook system for alert delivery
- [ ] Persistent alert history (database)

### Expected Outcome:

Enterprise-grade integration capabilities

---

# Next Steps: Phase 4

## Advanced Features (Priority 2)

### What to build:

- [ ] Alert batching to reduce frequency
- [ ] Alert deduplication across instances
- [ ] Alert correlation engine
- [ ] Time-based alert suppression

### Expected Outcome:

Reduced alert fatigue and smarter grouping

---

# Next Steps: Phase 5

## Operational Excellence (Priority 3)

### What to build:

- [ ] Comprehensive error handling
- [ ] Graceful shutdown procedures
- [ ] Configuration file support
- [ ] Multi-threaded processing
- [ ] Circuit breaker patterns

### Expected Outcome:

Production-ready reliability and resilience

---

# Next Steps: Phase 6

## Observability (Priority 3)

### What to build:

- [ ] Distributed tracing support
- [ ] Prometheus metrics export
- [ ] Debugging endpoints
- [ ] Event replay capability

### Expected Outcome:

Deep insights into system behavior and easy troubleshooting

---

# Testing Checklist

- [ ] Error thresholds at exact boundaries
- [ ] Rapid error spikes and escalations
- [ ] Sustained errors without escalation
- [ ] Error fluctuations within same level
- [ ] Recovery and state reset
- [ ] Timestamp precision and ordering
- [ ] Event pruning from window

---

# Performance Metrics

| Aspect | Performance |
|--------|-------------|
| Event Processing | O(1) per event |
| Window Maintenance | O(n) where n < 120 |
| Memory Usage | Bounded by window |
| Alert Generation | Immediate, minimal latency |

---

# Configuration

To modify thresholds, edit `ErrorSpikeRule::new()` in `event_spike_rule.rs`:

```rust
window: Duration::minutes(2),
high_threshold: 10,
critical_threshold: 25,
severe_threshold: 50,
```

---

# Support

**Questions or issues?**

1. Review inline code comments
2. Check event logs
3. Verify event timestamps and IDs
4. Profile if delays occur

---

**Document Version:** 1.0  
**Last Updated:** March 20, 2026  
**Status:** Current

