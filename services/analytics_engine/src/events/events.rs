use std::hash::Hash;
use uuid::Uuid;

use time::UtcDateTime;

#[derive(Debug, PartialEq, Eq, Hash, Clone, Copy)]
pub enum EventType {
    SystemMetrics,
}

#[derive(Debug, Clone)]
pub struct Event {
    pub event_id: Uuid,
    pub event_type: EventType,
    pub occurred_at: UtcDateTime,
    pub parent: Parent,
}

#[derive(Eq, Hash, PartialEq, Clone, Debug)]
pub struct Parent(pub String);