use dotenvy::dotenv;
use std::env;

#[derive(Debug, Clone)]
pub struct Config {
    pub redis_url: String,
    pub redis_stream_name: String,
    pub redis_group_name: String,
    pub redis_consumer_name: String,
    pub postgres_url: String,
}

impl Config {
    pub fn from_env() -> Self {
        dotenv().ok();
        Self {
            redis_url: env::var("REDIS_URL")
                .unwrap_or_else(|_| "redis://127.0.0.1:6379".to_string()),
            redis_stream_name: env::var("REDIS_STREAM_NAME")
                .unwrap_or_else(|_| "analytics_events".to_string()),
            redis_group_name: env::var("REDIS_GROUP_NAME")
                .unwrap_or_else(|_| "event_processor_group".to_string()),
            redis_consumer_name: env::var("REDIS_CONSUMER_NAME")
                .unwrap_or_else(|_| "instance_1".to_string()),
            postgres_url: env::var("POSTGRES_URL")
                .unwrap_or_else(|_| "postgres://localhost/analytics".to_string()),
        }
    }
}