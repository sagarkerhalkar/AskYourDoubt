# Production Scale Plan — Target: 50,000,000 Students

## Phase 1 — Laptop functional approval

- Run the included SQLite build side-by-side.
- Complete functional acceptance testing.
- Approve responsive UI on representative Android, iPhone, tablet, laptop, and desktop devices.
- Validate student, teacher, and admin flows.

## Phase 2 — Production foundation

- Replace SQLite with PostgreSQL.
- Move Flask session state to Redis.
- Move uploaded files and QR codes to object storage.
- Run the application with multiple production WSGI workers.
- Add reverse proxy, TLS, rate limiting, CSRF protection, and security headers.
- Add background jobs for exports and analytics.

## Phase 3 — Realtime architecture

- Replace one-second HTTP polling with managed WebSocket or Server-Sent Events infrastructure.
- Use Redis Streams, Kafka, or a cloud event bus to distribute doubt and vote updates.
- Partition traffic by institution/session.
- Protect hot sessions from vote storms using atomic Redis operations and durable event processing.

## Phase 4 — Global architecture

- Multi-region application deployment.
- Geo-routing and global CDN.
- Database replicas/sharding strategy.
- Regional object-storage replication.
- Automated failover and disaster recovery.

## Phase 5 — Verification

- Load test gradually from thousands to millions of concurrent virtual users.
- Soak test long-running sessions.
- Test failover, packet loss, regional outage, and database recovery.
- Penetration test authentication, file uploads, student privacy, and admin controls.
- Conduct accessibility and internationalisation review.

The included local test suite verifies application behaviour, not 50,000,000-user infrastructure capacity.
