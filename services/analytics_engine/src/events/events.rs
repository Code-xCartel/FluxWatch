use std::hash::Hash;
use uuid::Uuid;

use time::UtcDateTime;

#[derive(Debug, PartialEq, Eq, Hash, Clone, Copy)]
pub enum EventType {
    SystemMetric,
    UserLogin,
    UserLogout,
    OrderCreated,
    OrderCompleted,
    OrderCancelled,
    SessionStarted,
    SessionEnded,
}

#[derive(Debug, Clone)]
pub struct Event {
    pub id: Uuid,
    pub entity_type: String,
    pub entity_id: String,
    pub event_type: EventType,
    pub event_version: u32,
    pub occurred_at: UtcDateTime,
    pub created_at: UtcDateTime,
    pub updated_at: UtcDateTime,
    pub producer: String,
    pub actor_type: Option<String>,
    pub actor_id: Option<String>,
    pub context: Option<String>,
    pub payload: String,
    pub parent: Parent,
}

#[derive(Eq, Hash, PartialEq, Clone, Debug)]
pub struct Parent(pub String);