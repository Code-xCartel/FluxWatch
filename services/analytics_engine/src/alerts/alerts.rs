use crate::events::events::Parent;
use time::UtcDateTime;
use uuid::Uuid;

#[derive(Debug, PartialEq, PartialOrd, Clone, Copy)]
pub enum AlertLevel {
    High,
    Critical,
    Severe,
}

#[derive(Debug)]
pub enum AlertType {
    ErrorSpike,
}

#[derive(Debug)]
pub struct Alert {
    pub alert_type: AlertType,
    pub level: AlertLevel,
    pub message: String,
    pub triggered_at: UtcDateTime,
    pub event_ids: Vec<Uuid>,
    pub parent: Parent,
}

impl Alert {
    pub fn build_alert(
        alert_type: AlertType,
        level: AlertLevel,
        message: String,
        now: UtcDateTime,
        event_ids: Vec<Uuid>,
        parent: &Parent,
    ) -> Self {
        Self {
            alert_type,
            level,
            message,
            triggered_at: now,
            event_ids,
            parent: parent.clone(),
        }
    }
}
