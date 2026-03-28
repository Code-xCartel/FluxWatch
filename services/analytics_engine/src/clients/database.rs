use native_tls::TlsConnector;
use postgres::{Client, Error};
use postgres_native_tls::MakeTlsConnector;
use time::format_description::well_known::Iso8601;

use crate::alerts::{Alert, AlertLevel, AlertType};
use crate::clients::config::Config;

pub struct DatabaseClient {
    client: Client,
}

impl DatabaseClient {
    pub fn new(config: &Config) -> Result<Self, Box<dyn std::error::Error>> {
        let tls_connector = TlsConnector::new()?;
        let tls = MakeTlsConnector::new(tls_connector);
        let client = Client::connect(&config.postgres_url, tls)?;
        Ok(Self { client })
    }

    pub fn push_alert(&mut self, alert: &Alert) -> Result<(), Error> {
        let event_ids: Vec<String> = alert.event_ids.iter().map(|id| id.to_string()).collect();
        let triggered_at = alert
            .triggered_at
            .format(&Iso8601::DEFAULT)
            .expect("failed to format alert timestamp");

        self.client.execute(
            "INSERT INTO alerts (alert_type, level, message, triggered_at, event_ids, parent)
             VALUES ($1, $2, $3, $4, $5, $6)",
            &[
                &Self::alert_type_as_str(&alert.alert_type),
                &Self::alert_level_as_str(&alert.level),
                &alert.message,
                &triggered_at,
                &event_ids,
                &alert.parent.0,
            ],
        )?;

        Ok(())
    }

    fn alert_type_as_str(alert_type: &AlertType) -> &'static str {
        match alert_type {
            AlertType::ErrorSpike => "ErrorSpike",
        }
    }

    fn alert_level_as_str(alert_level: &AlertLevel) -> &'static str {
        match alert_level {
            AlertLevel::High => "High",
            AlertLevel::Critical => "Critical",
            AlertLevel::Severe => "Severe",
        }
    }
}
