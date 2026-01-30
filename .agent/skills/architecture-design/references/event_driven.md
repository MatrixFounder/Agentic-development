# Event-Driven Architecture

## Core Philosophy
Services communicate by emitting **Events** (facts that happened) rather than calling each other directly (Commands).

## Components

### 1. Producer
- The service that detects a state change and publishes an event.
- **Fire-and-Forget:** Does not wait for a response.

### 2. Broker / Event Bus
- The infrastructure that receives events and routes them to consumers.
- **Examples:** RabbitMQ, Kafka, AWS SNS/SQS, Redis Pub/Sub.

### 3. Consumer
- The service that subscribes to events and reacts.

## Key Concepts

### Idempotency
- **Rule:** Consumers MUST handle receiving the same event multiple times without side effects.
- **Why?** Networks fail, retries happen.
- **How?** Track `processed_event_ids` or design operations to be naturally idempotent (setting state vs incrementing).

### Async vs Sync
- **Sync (Request/Response):** Use for UI reads or when immediate confirmation is needed.
- **Async (Events):** Use for background processing, email sending, analytics, data synchronization.

### Dead Letter Queues (DLQ)
- **Problem:** What if a consumer fails to process an event?
- **Solution:** Move failed messages to a DLQ for manual inspection after N retries. Never block the main queue.

## Implementation Guide
1.  Define the **Event Schema** (JSON/Protobuf).
2.  Publish event in the **Producer** inside a transaction (Outbox Pattern) if data integrity is critical.
3.  Implement **Consumer** with retries and Idempotency checks.
