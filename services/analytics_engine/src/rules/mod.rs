mod engine;
mod event_spike_rule;

use crate::alerts::Alert;
use crate::events::Event;

use crate::events::events::Parent;
pub use engine::RuleEngine;
pub use event_spike_rule::ErrorSpikeRule;

pub trait EventRule {
    fn process(&mut self, event: Event) -> Option<Alert>;

    // implementation of this trait method is not required,
    // it's just here to enforce parent struct field in each new rule
    fn parent(&self) -> &Parent;
}
