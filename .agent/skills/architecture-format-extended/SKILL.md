---
name: architecture-format-extended
description: Extended architecture templates with full examples. Imports architecture-format-core for base structure.
version: 1.0
tier: 2
requires: architecture-format-core
---

# Architecture Document Structure (Extended)

> [!NOTE]
> This skill provides **FULL** templates with detailed examples.
> It extends `architecture-format-core` with comprehensive sections 3-10.

## When to Load This Skill

| Condition | Action |
|-----------|--------|
| Creating NEW system from scratch | ✅ Load this skill |
| Major refactor (>3 components changed) | ✅ Load this skill |
| Sophisticated requirement / complex task | ✅ Load this skill |
| User explicitly requests full template | ✅ Load this skill |
| Minor architecture update | ❌ Use `architecture-format-core` only |

---

## 3. System Components (Extended Examples)

### Detailed Component Template

**Component Name:** [Example, "User Service"]

**Type:** [Backend service / Frontend / Database / Message Queue / etc.]

**Purpose:** [Why needed]

**Implemented Functions:** [Links to functions from functional architecture]

**Technologies:** [Programming language, frameworks]

**Interfaces:**
- Inbound: [Who and how accesses this component]
- Outbound: [Who and how this component accesses]

**Dependencies:**
- External libraries
- Other system components
- External services

---

## 4. Data Model (Full)

### 4.1. Conceptual Data Model

Description of main entities and their relationships at a high level.

**Entities:**

#### Entity: [Name, e.g., "User"]

**Description:** [What this entity represents]

**Attributes:**
- `id` (UUID) — unique identifier
- `email` (String, unique) — user email
- `password_hash` (String) — password hash
- `created_at` (DateTime) — creation date
- `status` (Enum: pending, active, blocked) — account status

**Relationships:**
- One User has many Sessions (1:N)
- One User has one Profile (1:1)

**Business Rules:**
- Email must be unique
- Password must be at least 8 characters
- Default status — pending

---

#### Entity: [Next entity]
...

### 4.2. Logical Data Model

More detailed description considering storage technology.

**For Relational DB:**

#### Table: `users`

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | UUID | PRIMARY KEY | Unique identifier |
| email | VARCHAR(255) | UNIQUE, NOT NULL | User email |
| password_hash | VARCHAR(255) | NOT NULL | Bcrypt password hash |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Creation date |
| updated_at | TIMESTAMP | NOT NULL, DEFAULT NOW() | Update date |
| status | VARCHAR(20) | NOT NULL, DEFAULT 'pending' | Account status |

**Indexes:**
- PRIMARY KEY on `id`
- UNIQUE INDEX on `email`
- INDEX on `status` (for filtering)

**Foreign Keys:**
- None

---

**For NoSQL DB:**

#### Collection: `users`

```json
{
  "_id": "ObjectId",
  "email": "string (unique)",
  "password_hash": "string",
  "created_at": "ISODate",
  "updated_at": "ISODate",
  "status": "string (enum: pending, active, blocked)",
  "profile": {
    "first_name": "string",
    "last_name": "string",
    "avatar_url": "string"
  },
  "sessions": [
    {
      "token": "string",
      "created_at": "ISODate",
      "expires_at": "ISODate"
    }
  ]
}
```

**Indexes:**
- Unique index on `email`
- Index on `status`
- TTL index on `sessions.expires_at`

### 4.3. Data Model Diagram

```
[ER-diagram in PlantUML format]

Example:
┌─────────────┐         ┌─────────────┐
│    User     │         │   Session   │
├─────────────┤         ├─────────────┤
│ id (PK)     │────────<│ user_id(FK) │
│ email       │    1:N  │ token       │
│ password    │         │ expires_at  │
└─────────────┘         └─────────────┘
```

### 4.4. Migrations and Versioning

**Migration Strategy:**
[How DB schema changes will be executed]

**For modification of existing system:**
- Which tables/collections to add
- Which fields to add to existing tables
- Which indexes to create
- Data migration plan (if needed)

---

## 5. Interfaces

### 5.1. External APIs

For each external API describe:

#### API: [Name, e.g. "User Management API"]

**Protocol:** REST / GraphQL / gRPC / WebSocket

**Base URL:** `/api/v1/users`

**Authentication:** JWT Bearer Token

**Endpoints:**

##### POST /register

**Description:** New user registration

**Related Use Case:** UC-01

**Request:**
```json
{
  "email": "string (required, email format)",
  "password": "string (required, min 8 chars)",
  "password_confirmation": "string (required)"
}
```

**Response 201 Created:**
```json
{
  "user_id": "uuid",
  "email": "string",
  "status": "pending",
  "message": "Confirmation email sent"
}
```

**Response 400 Bad Request:**
```json
{
  "error": "validation_error",
  "details": {
    "email": ["Email already exists"],
    "password": ["Password too short"]
  }
}
```

**Response 500 Internal Server Error:**
```json
{
  "error": "internal_error",
  "message": "Failed to send confirmation email"
}
```

---

##### GET /users/{id}

[Description of next endpoint]

---

### 5.2. Internal Interfaces

Description of interaction between system components.

#### Interface: UserService → EmailService

**Protocol:** Message Queue (RabbitMQ)

**Exchange:** `notifications`

**Routing Key:** `email.confirmation`

**Message Format:**
```json
{
  "user_id": "uuid",
  "email": "string",
  "confirmation_token": "string",
  "template": "user_confirmation"
}
```

---

### 5.3. Integrations with External Systems

If system integrates with external services:

#### Integration: Email Service (SendGrid)

**Purpose:** Sending email notifications

**Protocol:** REST API

**Authentication:** API Key

**Endpoints Used:**
- POST /v3/mail/send — send email

**Error Handling:**
- Retry with exponential backoff
- Maximum 3 attempts
- Logging of failed sends

---

## 6. Technology Stack

### 6.1. Backend

**Programming Language:** [Python / Java / Node.js / etc.]

**Framework:** [Django / Spring Boot / Express / etc.]

**Justification:**
[Why these technologies were chosen]

### 6.2. Frontend (if applicable)

**Framework:** [React / Vue / Angular / etc.]

**Justification:**

### 6.3. Database

**Type:** [PostgreSQL / MongoDB / Redis / etc.]

**Justification:**

### 6.4. Infrastructure

**Containerization:** Docker

**Orchestration:** Kubernetes / Docker Compose

**Message Queue:** RabbitMQ / Kafka / Redis

**Caching:** Redis / Memcached

**Monitoring:** Prometheus + Grafana

**Logging:** ELK Stack / Loki

### 6.5. For Modification of Existing Project

**Used Technologies:**
[List of technologies already in project]

**New Technologies:**
[What needs to be added and why]

**Compatibility:**
[How new technologies integrate with existing ones]

---

## 7. Security

### 7.1. Authentication and Authorization

**Auth Mechanism:** JWT / OAuth 2.0 / Session-based

**Password Storage:** Bcrypt / Argon2

**Session Management:**
- Token lifetime
- Refresh tokens
- Token revocation mechanism

### 7.2. Data Protection

**Encryption:**
- At rest: DB encryption
- In transit: TLS/SSL

**Personal Data:**
- What data is considered personal
- How it is protected
- GDPR compliance (if applicable)

### 7.3. Attack Protection

**OWASP Top 10:**
- SQL Injection: using parameterized queries
- XSS: input sanitization
- CSRF: CSRF tokens
- Etc.

**Rate Limiting:**
- Request limits
- DDoS protection

---

## 8. Scalability and Performance

### 8.1. Scaling Strategy

**Horizontal Scaling:**
- Which components can be scaled horizontally
- How load balancing is ensured

**Vertical Scaling:**
- Which components require vertical scaling

### 8.2. Caching

**What is cached:**
- Static data
- Frequent query results
- User sessions

**Cache Invalidation Strategy:**

### 8.3. DB Optimization

**Indexes:**
[Which indexes are critical for performance]

**Partitioning:**
[If applicable]

**Replication:**
[Master-Slave, Master-Master]

---

## 9. Reliability and Fault Tolerance

### 9.1. Error Handling

**Strategy:**
- Graceful degradation
- Circuit breaker pattern
- Retry logic

### 9.2. Backup

**What is backed up:**
- Database
- User files
- Configuration

**Backup Frequency:**

**Backup Storage:**

### 9.3. Monitoring and Alerting

**Metrics:**
- API response time
- Error count
- Resource usage

**Alerts:**
- Conditions for sending
- Where sent

---

## 10. Deployment

### 10.1. Environments

**Development:**
[Description of dev environment]

**Staging:**
[Description of staging environment]

**Production:**
[Description of prod environment]

### 10.2. CI/CD Pipeline

**Stages:**
1. Build
2. Unit Tests
3. Integration Tests
4. Deploy to Staging
5. E2E Tests
6. Deploy to Production

**Tools:**
- CI/CD: GitHub Actions / GitLab CI / Jenkins
- Deployment: Kubernetes / Docker Swarm / AWS ECS

### 10.3. Configuration

**Configuration Management:**
- Environment variables
- Config files
- Secrets management (Vault / AWS Secrets Manager)

### 10.4. Deployment Instructions

**For New Project:**
1. Step 1: [Description]
2. Step 2: [Description]
...

**For Modification of Existing Project:**
1. Step 1: [Description of changes]
2. Step 2: [DB migrations]
3. Step 3: [Configuration update]
...
