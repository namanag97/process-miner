# ⚠️ MOCK DATA NOTICE

> [!CAUTION] > **This codebase contains mock implementations that are NOT production-ready.**
> The following components must be replaced before deploying to production.

---

## Mock Implementations Inventory

### Backend Mocks (10 Components)

| File                      | Mock Component            | Current Behavior           | Production Requirement     |
| ------------------------- | ------------------------- | -------------------------- | -------------------------- |
| `auth_service.py`         | `MOCK_USERS` dict         | In-memory user storage     | Real database + OAuth/OIDC |
| `auth_service.py`         | `AuthService`             | Accepts any password       | Proper password hashing    |
| `integration_service.py`  | `MockSAPConnector`        | Returns fake SAP data      | SAP RFC/BAPI integration   |
| `integration_service.py`  | `MockSalesforceConnector` | Returns fake SF data       | Salesforce API integration |
| `integration_service.py`  | `MockJiraConnector`       | Returns fake JIRA data     | JIRA REST API integration  |
| `integration_service.py`  | `MockDatabaseConnector`   | Returns fake DB data       | Real JDBC/ODBC connections |
| `prediction_service.py`   | `PredictionService`       | Statistical approximations | ML model inference         |
| `notification_service.py` | Email handler             | Logs to console            | SMTP/SendGrid integration  |
| `notification_service.py` | Webhook handler           | Logs to console            | HTTP POST delivery         |
| `event_bus.py`            | `EventBus`                | In-memory pub/sub          | Kafka/RabbitMQ             |
| `task_queue.py`           | `TaskQueue`               | In-memory queue            | Celery/RabbitMQ            |

### Frontend Mocks (3 Components)

| File                | Mock Component       | Fix Required                        |
| ------------------- | -------------------- | ----------------------------------- |
| `Dashboard.tsx`     | Mock dashboard stats | Connect to `/api/v1/analytics`      |
| `ProcessList.tsx`   | Mock process list    | Connect to `/api/v1/processes`      |
| `ProcessDetail.tsx` | Mock process data    | Connect to `/api/v1/processes/{id}` |

---

## File Locations

### Backend Mock Files

```
backend/src/application/generic/
├── auth_service.py          # Mock authentication
├── integration_service.py   # Mock external connectors
└── notification_service.py  # Mock notifications

backend/src/application/core/
└── prediction_service.py    # Mock ML predictions

backend/src/infrastructure/
├── messaging/event_bus.py   # Mock Kafka
└── workers/task_queue.py    # Mock RabbitMQ
```

### Frontend Mock Files

```
frontend/apps/process-mining/src/pages/
├── Dashboard.tsx            # Mock data at line 39
├── ProcessList.tsx          # Mock data at line 19
└── ProcessDetail.tsx        # Mock data at line 10
```

---

## Recommended Migration Path

1. **Authentication** → Replace with Keycloak/Auth0/Firebase Auth
2. **Message Queue** → Deploy Kafka/RabbitMQ with connection pooling
3. **Integrations** → Implement real API clients with retries
4. **Notifications** → Add SendGrid/Mailgun for email, webhook delivery
5. **ML Predictions** → Deploy trained models with MLflow/BentoML
6. **Frontend** → Wire pages to SDK clients (already available)

---

_Generated: 2025-12-29_
