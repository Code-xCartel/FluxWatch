use crate::alerts::{Alert, AlertLevel, AlertType};
use crate::events::Event;
use crate::rules::EventRule;

use crate::events::events::Parent;
use time::{Duration, UtcDateTime};
use uuid::Uuid;

#[derive(Debug)]
enum State {
    INITIAL,
    ESCALATION,
    SUSTAINED,
}

pub struct ErrorSpikeRule {
    pub events: Vec<Event>,
    pub window: Duration,

    // thresholds
    pub high_threshold: usize,
    pub critical_threshold: usize,
    pub severe_threshold: usize,

    // control
    pub last_alert_time: Option<UtcDateTime>,
    pub last_alert_level: Option<AlertLevel>,
    pub last_sustained_count: Option<usize>,

    //identity
    pub parent: Parent,
}

impl ErrorSpikeRule {
    pub fn new(parent: Parent) -> Self {
        Self {
            events: Vec::new(),
            window: Duration::minutes(2),
            high_threshold: 10,
            critical_threshold: 25,
            severe_threshold: 50,
            last_alert_time: None,
            last_alert_level: None,
            last_sustained_count: None,

            parent,
        }
    }

    fn get_level(&self, count: usize) -> Option<AlertLevel> {
        if count >= self.severe_threshold {
            Some(AlertLevel::Severe)
        } else if count >= self.critical_threshold {
            Some(AlertLevel::Critical)
        } else if count >= self.high_threshold {
            Some(AlertLevel::High)
        } else {
            None
        }
    }

    fn get_message(&self, count: usize, state: State) -> String {
        // Calculate actual time span from oldest to newest event
        let time_span = if self.events.len() > 1 {
            let oldest = self.events.first().unwrap();
            let newest = self.events.last().unwrap();
            (newest.occurred_at - oldest.occurred_at).whole_seconds()
        } else {
            0
        };

        format!("[{:?}] {} errors in last {}s", state, count, time_span)
    }

    fn get_event_ids(&self) -> Vec<Uuid> {
        self.events.iter().map(|e| e.event_id).collect()
    }
}

impl EventRule for ErrorSpikeRule {
    fn process(&mut self, event: Event) -> Option<Alert> {
        let now = event.occurred_at;

        self.events.push(event);
        self.events.retain(|t| t.occurred_at > now - self.window);

        let count = self.events.len();

        // reset alert state if we drop below high threshold
        if count < self.high_threshold {
            self.last_alert_level = None;
            self.last_alert_time = None;
            self.last_sustained_count = None;
            return None;
        }

        let current_level = match self.get_level(count) {
            Some(level) => level,
            None => return None,
        };

        if let Some(last_level) = self.last_alert_level {
            // alert level increased
            if current_level > last_level {
                self.last_alert_level = Some(current_level);
                self.last_alert_time = Some(now);
                self.last_sustained_count = None;

                return Some(Alert::build_alert(
                    AlertType::ErrorSpike,
                    current_level,
                    self.get_message(count, State::ESCALATION),
                    now,
                    self.get_event_ids(),
                    self.parent(),
                ));
            }
        } else {
            // initial threshold level
            self.last_alert_level = Some(current_level);
            self.last_alert_time = Some(now);
            self.last_sustained_count = None;

            return Some(Alert::build_alert(
                AlertType::ErrorSpike,
                current_level,
                self.get_message(count, State::INITIAL),
                now,
                self.get_event_ids(),
                self.parent(),
            ));
        }

        // send SUSTAINED alert if window passed and count has changed
        if let Some(last_time) = self.last_alert_time {
            if now - last_time >= self.window {
                let should_alert = self.last_sustained_count.is_none()
                    || self.last_sustained_count.map_or(false, |lc| count != lc);

                if should_alert {
                    self.last_alert_time = Some(now);
                    self.last_sustained_count = Some(count);

                    return Some(Alert::build_alert(
                        AlertType::ErrorSpike,
                        current_level,
                        self.get_message(count, State::SUSTAINED),
                        now,
                        self.get_event_ids(),
                        self.parent(),
                    ));
                }
            }
        }

        None
    }

    fn parent(&self) -> &Parent {
        &self.parent
    }
}
