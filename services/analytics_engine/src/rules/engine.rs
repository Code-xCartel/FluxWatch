use std::collections::HashMap;

use super::{ErrorSpikeRule, EventRule};
use crate::events::EventType;
use crate::events::events::Parent;

pub struct RuleEngine {
    rules: HashMap<(EventType, Parent), Box<dyn EventRule>>,
}

impl RuleEngine {
    pub fn new() -> Self {
        Self {
            rules: HashMap::new(),
        }
    }

    fn _get_rule_from_type(event_type: &EventType, parent: Parent) -> Box<dyn EventRule> {
        match event_type {
            EventType::SystemMetric => Box::new(ErrorSpikeRule::new(parent)),
            // Add more event types and their corresponding rules here
            _ => panic!("No rule defined for event type: {:?}", event_type),
        }
    }

    pub fn rule_for(
        &mut self,
        event_type: &EventType,
        parent: &Parent,
    ) -> &mut (dyn EventRule + 'static) {
        let key = (event_type.clone(), parent.clone());

        // not using &self to fetch rule since that would lead to immutable borrow,
        // and we need mutable borrow to insert if rule doesn't exist
        let rule = self
            .rules
            .entry(key)
            .or_insert_with(|| Self::_get_rule_from_type(event_type, parent.clone()));
        rule.as_mut()
    }
}
