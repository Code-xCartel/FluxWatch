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
        let id_str: String =
            FromRedisValue::from_redis_value(event_data.get("id")?.clone()).ok()?;
        let entity_type: String =
            FromRedisValue::from_redis_value(event_data.get("entity_type")?.clone()).ok()?;
        let entity_id: String =
            FromRedisValue::from_redis_value(event_data.get("entity_id")?.clone()).ok()?;
        let event_type_str: String =
            FromRedisValue::from_redis_value(event_data.get("event_type")?.clone()).ok()?;
        let event_version_str: String =
            FromRedisValue::from_redis_value(event_data.get("event_version")?.clone()).ok()?;
        let occurred_at_str: String =
            FromRedisValue::from_redis_value(event_data.get("occurred_at")?.clone()).ok()?;
        let created_at_str: String =
            FromRedisValue::from_redis_value(event_data.get("created_at")?.clone()).ok()?;
        let updated_at_str: String =
            FromRedisValue::from_redis_value(event_data.get("updated_at")?.clone()).ok()?;
        let producer: String =
            FromRedisValue::from_redis_value(event_data.get("producer")?.clone()).ok()?;
        let actor_type_str: String =
            FromRedisValue::from_redis_value(event_data.get("actor_type")?.clone()).ok()?;
        let actor_id_str: String =
            FromRedisValue::from_redis_value(event_data.get("actor_id")?.clone()).ok()?;
        let context_str: String =
            FromRedisValue::from_redis_value(event_data.get("context")?.clone()).ok()?;
        let payload: String =
            FromRedisValue::from_redis_value(event_data.get("payload")?.clone()).ok()?;
        let parent_str: String =
            FromRedisValue::from_redis_value(event_data.get("parent")?.clone()).ok()?;

        let id = Uuid::parse_str(&id_str).ok()?;

        let event_type = match event_type_str.as_str() {
            "system.metric" => EventType::SystemMetric,
            "user.login" => EventType::UserLogin,
            "user.logout" => EventType::UserLogout,
            "order.created" => EventType::OrderCreated,
            "order.completed" => EventType::OrderCompleted,
            "order.cancelled" => EventType::OrderCancelled,
            "session.started" => EventType::SessionStarted,
            "session.ended" => EventType::SessionEnded,
            _ => {
                eprintln!("Unknown event type: {}", event_type_str);
                return None;
            }
        };

        let event_version: u32 = event_version_str.parse().ok()?;
        let occurred_at = UtcDateTime::parse(&occurred_at_str, &Iso8601::DEFAULT).ok()?;
        let created_at = UtcDateTime::parse(&created_at_str, &Iso8601::DEFAULT).ok()?;
        let updated_at = UtcDateTime::parse(&updated_at_str, &Iso8601::DEFAULT).ok()?;

        let actor_type = if actor_type_str.is_empty() {
            None
        } else {
            Some(actor_type_str)
        };
        let actor_id = if actor_id_str.is_empty() {
            None
        } else {
            Some(actor_id_str)
        };
        let context = if context_str.is_empty() {
            None
        } else {
            Some(context_str)
        };

        Some(Event {
            id,
            entity_type,
            entity_id,
            event_type,
            event_version,
            occurred_at,
            created_at,
            updated_at,
            producer,
            actor_type,
            actor_id,
            context,
            payload,
            parent: Parent(parent_str),
        })
    }
}
