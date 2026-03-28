use crate::clients::Config;
use crate::events::events::Parent;
use crate::events::{Event, EventType};
use redis::streams::{StreamReadOptions, StreamReadReply};
use redis::{Client, Commands, Connection, FromRedisValue, RedisResult, Value};
use std::collections::HashMap;
use time::{UtcDateTime, format_description::well_known::Iso8601};
use uuid::Uuid;

pub struct RedisClient {
    connection: Connection,
    options: StreamReadOptions,

    stream: String,
    group: String,

    ack_list: Vec<String>,
}

impl RedisClient {
    pub fn new(config: &Config) -> RedisResult<Self> {
        let client = Client::open(config.redis_url.clone())?;
        let connection = client.get_connection()?;

        let (stream, group, consumer) = (
            config.redis_stream_name.clone(),
            config.redis_group_name.clone(),
            config.redis_consumer_name.clone(),
        );

        let options = StreamReadOptions::default()
            .group(&group, &consumer)
            .count(10)
            .block(5000); // Block for 5 seconds if no messages are available

        Ok(Self {
            connection,
            options,

            stream,
            group,

            ack_list: vec![],
        })
    }

    pub fn poll(&mut self) -> RedisResult<Vec<Event>> {
        let reply: StreamReadReply =
            self.connection
                .xread_options(&[&self.stream], &[">"], &self.options)?;

        let mut events = Vec::new();

        if let Some(key) = reply.keys.first() {
            for msg in &key.ids {
                let event_data: HashMap<String, Value> = msg.map.clone();

                if let Some(event) = self.parse_redis_event(event_data) {
                    events.push(event);
                    self.ack_list.push(msg.id.clone())
                }
            }
        } else {
            println!("No new events found")
        }

        Ok(events)
    }

    pub fn acknowledge(&mut self) {
        for id in self.ack_list.iter() {
            let _: RedisResult<String> = redis::cmd("XACK")
                .arg(&self.stream)
                .arg(&self.group)
                .arg(id)
                .query(&mut self.connection);
        }

        println!("Acknowledged {} events", self.ack_list.len());
        self.ack_list.clear();
    }

    fn parse_redis_event(&self, event_data: HashMap<String, Value>) -> Option<Event> {
        // Extract and convert each field from Redis values using FromRedisValue trait
        let event_id_str: String =
            FromRedisValue::from_redis_value(event_data.get("event_id")?.clone()).ok()?;
        let event_type_str: String =
            FromRedisValue::from_redis_value(event_data.get("event_type")?.clone()).ok()?;
        let parent_str: String =
            FromRedisValue::from_redis_value(event_data.get("parent")?.clone()).ok()?;
        let occurred_at_str: String =
            FromRedisValue::from_redis_value(event_data.get("occurred_at")?.clone()).ok()?;

        // Parse event_id as UUID
        let event_id = Uuid::parse_str(&event_id_str).ok()?;

        // Parse event_type
        let event_type = match event_type_str.as_str() {
            "SystemMetrics" => EventType::SystemMetrics,
            _ => {
                eprintln!("Unknown event type: {}", event_type_str);
                return None;
            }
        };

        // Parse occurred_at as UtcDateTime
        let occurred_at = UtcDateTime::parse(&occurred_at_str, &Iso8601::DEFAULT).ok()?;
        let parent = Parent(parent_str);

        Some(Event {
            event_id,
            event_type,
            parent,
            occurred_at,
        })
    }
}
