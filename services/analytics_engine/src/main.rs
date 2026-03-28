mod alerts;
mod clients;
mod events;
mod rules;

use clients::{Config, DatabaseClient, RedisClient};
use rules::RuleEngine;

fn main() {
    let config = Config::from_env();

    // Initialize Redis client
    let mut redis_client = match RedisClient::new(&config) {
        Ok(client) => {
            println!("Connected to Redis successfully");
            client
        }
        Err(e) => {
            eprintln!("Failed to connect to Redis: {}", e);
            eprintln!("Make sure Redis is running");
            return;
        }
    };

    // Initialize Database client
    let mut db_client = match DatabaseClient::new(&config) {
        Ok(db_client) => {
            println!("Connected to Database successfully");
            db_client
        }
        Err(e) => {
            eprintln!("Failed to connect to database: {}", e);
            eprintln!("Make sure postgres is running");
            return;
        }
    };

    // Initialize Rule Engine
    let mut rule_engine = RuleEngine::new();

    loop {
        println!("Polling for events...");
        match redis_client.poll() {
            Ok(events) => {
                for event in events {
                    println!(
                        "Processing event: {} for user: {:?}",
                        event.event_id, event.parent
                    );

                    let rule = rule_engine.rule_for(&event.event_type, &event.parent);
                    if let Some(alert) = rule.process(event) {
                        println!("ALERT: {:?}", alert);
                        db_client.push_alert(&alert).unwrap_or_else(|e| {
                            eprintln!("Failed to push alert to database: {}", e)
                        });
                    }
                }
            }
            Err(e) => {
                eprintln!("Failed redis connection: {}", e);
            }
        }

        redis_client.acknowledge();
    }
}
