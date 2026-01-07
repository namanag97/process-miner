# Error Handling & Logging Strategy

> **Version:** 1.0
> **Last Updated:** 2026-01-07
> **Purpose:** Comprehensive guide for error handling, user notifications, and intelligent DevConsole logging

---

## Table of Contents

1. [Overview](#overview)
2. [Error Classification](#error-classification)
3. [Error Boundaries](#error-boundaries)
4. [Notification Strategy](#notification-strategy)
5. [DevConsole Logging](#devconsole-logging)
6. [API Error Handling](#api-error-handling)
7. [Best Practices](#best-practices)
8. [Implementation Examples](#implementation-examples)

---

## Overview

Our error handling strategy uses **4 layers** of defense:

1. **Error Boundaries** - Catch React rendering errors at feature level
2. **API Error Interceptors** - Handle network/API failures consistently
3. **Query Error Callbacks** - React Query error handling with retries
4. **User Notifications** - Toast messages for transient errors

All errors are logged to **DevConsole** with **importance scoring (1-5)** for intelligent filtering during development and debugging.

---

## Error Classification

We classify errors into **4 categories** based on severity and handling:

### 1. **Transient Errors** (Network, Timeout)
- **HTTP Status:** 408, 429, 503, 504
- **User Experience:** Toast notification with "Retry" button
- **Logging:** Importance 3-4 (High if user-initiated)
- **Recovery:** Automatic retry with exponential backoff

**Example:**
```typescript
// Network timeout
devLog.error('API', 'Request timeout', {
  url: '/api/v1/datasets',
  duration: 30000,
  retryCount: 2
});
// Importance: 4 (High - blocks user action)
```

### 2. **Validation Errors** (Bad User Input)
- **HTTP Status:** 400, 422
- **User Experience:** Inline form errors (red text below field)
- **Logging:** Importance 2 (Low - expected user mistakes)
- **Recovery:** User corrects input and resubmits

**Example:**
```typescript
// Form validation error
devLog.info('Form:ProjectCreate', 'Validation failed', {
  fields: ['name', 'description'],
  errors: { name: 'Required', description: 'Min 10 characters' }
});
// Importance: 2 (Low - normal form interaction)
```

### 3. **Authorization Errors** (Permission Denied)
- **HTTP Status:** 401, 403
- **User Experience:** Modal dialog with "Contact Admin" or "Re-login"
- **Logging:** Importance 5 (Critical - security related)
- **Recovery:** User re-authenticates or contacts admin

**Example:**
```typescript
// Permission denied
devLog.error('Auth', 'Access denied to workspace', {
  userId: 'user-123',
  workspaceId: 'ws-456',
  requiredRole: 'editor',
  actualRole: 'viewer',
  action: 'DELETE_DATASET'
});
// Importance: 5 (Critical - security violation)
```

### 4. **Critical Errors** (500, Unknown Exceptions)
- **HTTP Status:** 500, 502, 503 (persistent)
- **User Experience:** Error boundary fallback screen
- **Logging:** Importance 5 (Critical - requires investigation)
- **Recovery:** Page reload or "Go Home"

**Example:**
```typescript
// React component crash
devLog.error('Feature:Explorer', 'Component render error', {
  error: 'Cannot read property of undefined',
  stack: error.stack,
  location: '/workspace/ws-001/data/ds-123/explorer',
  componentStack: errorInfo.componentStack
});
// Importance: 5 (Critical - breaks feature)
```

---

## Error Boundaries

### Feature-Level Boundaries

All 7 features have error boundaries:

- **Explorer** - Process exploration and filtering
- **Discovery** - Process model discovery
- **Analytics** - Performance analytics and metrics
- **AI** - AI predictions and insights
- **KPI** - KPI dashboards
- **Projects** - Project and workspace management
- **Upload Wizard** - Dataset upload and mapping

**Implementation:**
```tsx
import { ErrorBoundary } from 'react-error-boundary';
import { FeatureErrorFallback } from '@/shared/ui';

export function ExplorerRoutes() {
  return (
    <ErrorBoundary
      fallbackRender={({ error, resetErrorBoundary }) => (
        <FeatureErrorFallback
          error={error}
          resetError={resetErrorBoundary}
          featureName="Process Explorer"
        />
      )}
      onError={(error) => console.error('[Explorer] Error:', error)}
    >
      <Routes>
        {/* feature routes */}
      </Routes>
    </ErrorBoundary>
  );
}
```

### Logging in Error Boundaries

`FeatureErrorFallback` automatically logs to DevConsole:

```typescript
// Logs on error
devLog.error(
  `Feature:${featureName}`,
  `Feature error boundary caught: ${error.message}`,
  {
    error: error.message,
    stack: error.stack,
    featureName,
    location: window.location.pathname,
    timestamp: new Date().toISOString(),
  }
);

// Logs on user action
devLog.action(
  `Feature:${featureName}`,
  'User clicked Retry on error fallback',
  { featureName, location: window.location.pathname }
);
```

---

## Notification Strategy

### Decision Tree

```
Error Occurs
  │
  ├─ Is it a network/timeout error?
  │  └─ YES → Toast notification with "Retry" button
  │         → Log importance: 4
  │
  ├─ Is it a validation error (400)?
  │  └─ YES → Inline form error (red text)
  │         → Log importance: 2
  │
  ├─ Is it an auth error (401/403)?
  │  └─ YES → Modal dialog "Access Denied"
  │         → Log importance: 5
  │         → Redirect to login or contact admin
  │
  ├─ Is it a 404 (not found)?
  │  └─ YES → Empty state component
  │         → "No data available" message
  │         → Log importance: 3
  │
  └─ Is it a 500+ error or component crash?
     └─ YES → Error boundary fallback screen
            → "Something went wrong" UI
            → Log importance: 5
            → Offer "Retry" or "Go Home"
```

### Toast Notifications (message API)

Use Ant Design's `message` for transient errors:

```typescript
import { message } from 'antd';

// Error toast
message.error({
  content: 'Failed to load datasets. Please try again.',
  duration: 5,
  key: 'dataset-load-error', // Prevents duplicate toasts
});

// Success toast
message.success('Dataset uploaded successfully!');

// With action button
message.error({
  content: (
    <>
      Network error. <Button type="link" onClick={retry}>Retry</Button>
    </>
  ),
  duration: 0, // Manual dismiss
});
```

---

## DevConsole Logging

### Importance Scoring

Every log entry receives an **importance score (1-5)**:

| Score | Level | Examples | Visibility |
|-------|-------|----------|------------|
| **5** | Critical | Errors, 500s, crashes, auth failures | Always visible |
| **4** | High | User actions, mutations, slow requests (>1s) | Focus Mode + All |
| **3** | Medium | API responses (2xx), state changes, queries | All Mode only |
| **2** | Low | API requests (pending), perf logs | All Mode only |
| **1** | Noise | Heartbeats, polling, background metrics | Disabled in Focus Mode |

### devLog API

```typescript
import { devLog } from '@/shared/ui';

// Info logs (importance: 2-3)
devLog.info('DatasetList', 'Fetching datasets', { page: 1, limit: 20 });

// User actions (importance: 4, starts correlation)
devLog.action('ProjectCreate', 'User clicked Create Project', {
  projectName: 'New Project',
  workspaceId: 'ws-123'
});

// State changes (importance: 3)
devLog.state('FilterPanel', 'Applied filters', {
  minFrequency: 5,
  activities: ['Submit', 'Approve'],
  dateRange: ['2024-01-01', '2024-12-31']
});

// Errors (importance: 5)
devLog.error('Discovery', 'Failed to discover model', {
  error: 'Inductive Miner failed',
  datasetId: 'ds-456',
  algorithm: 'inductive',
  params: { noiseThreshold: 0.2 }
});

// API requests (importance: 2, tracked until response)
devLog.apiRequest('POST', '/api/v1/datasets', bodyData, headers);

// API responses (importance: 3-5 based on status)
devLog.apiResponse('POST', '/api/v1/datasets', 201, 1234, responseData);
```

### Correlation IDs

For tracking related logs across user flows:

```typescript
// User clicks "Discover Model" button
devLog.action('Discovery', 'User started discovery', { algorithm: 'inductive' });
// Correlation started automatically

// All subsequent logs in this flow will share correlationId
devLog.apiRequest('POST', '/api/v1/discovery/discover', { algorithm: 'inductive' });
// → correlationId: "discovery-1735123456"

devLog.apiResponse('POST', '/api/v1/discovery/discover', 200, 5432, model);
// → correlationId: "discovery-1735123456"

devLog.state('Discovery', 'Model loaded', { modelId: 'model-789' });
// → correlationId: "discovery-1735123456"
```

### Request Flow Timeline

DevConsole automatically tracks:
- **Pending requests** - Shows duration, detects stuck requests (>30s)
- **Request/response pairs** - Links API request to response
- **Slow requests** - Highlights requests >1s (importance +1)

---

## API Error Handling

### React Query Error Handling

```typescript
import { useQuery } from '@tanstack/react-query';
import { message } from 'antd';
import { devLog } from '@/shared/ui';

function useDatasets() {
  return useQuery({
    queryKey: ['datasets'],
    queryFn: async () => {
      devLog.apiRequest('GET', '/api/v1/datasets');
      const start = Date.now();

      try {
        const response = await fetch('/api/v1/datasets');
        const duration = Date.now() - start;

        if (!response.ok) {
          const error = await response.json();
          devLog.apiResponse('GET', '/api/v1/datasets', response.status, duration, error);
          throw new Error(error.message || 'Failed to fetch datasets');
        }

        const data = await response.json();
        devLog.apiResponse('GET', '/api/v1/datasets', 200, duration, data);
        return data;
      } catch (error) {
        devLog.error('Datasets', 'API call failed', {
          url: '/api/v1/datasets',
          error: error.message,
          duration: Date.now() - start
        });
        throw error;
      }
    },

    // Retry configuration
    retry: (failureCount, error) => {
      // Don't retry validation errors
      if (error.message.includes('400')) return false;
      // Retry transient errors up to 3 times
      return failureCount < 3;
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),

    // Error callback
    onError: (error) => {
      message.error({
        content: `Failed to load datasets: ${error.message}`,
        key: 'datasets-error',
        duration: 5,
      });
    },
  });
}
```

### Mutation Error Handling

```typescript
import { useMutation, useQueryClient } from '@tanstack/react-query';

function useCreateProject() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (project: { name: string; description: string }) => {
      devLog.action('Projects', 'Creating project', project);
      devLog.apiRequest('POST', '/api/v1/projects', project);

      const start = Date.now();
      const response = await fetch('/api/v1/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(project),
      });

      const duration = Date.now() - start;
      const data = await response.json();

      if (!response.ok) {
        devLog.apiResponse('POST', '/api/v1/projects', response.status, duration, data);
        throw new Error(data.message);
      }

      devLog.apiResponse('POST', '/api/v1/projects', 201, duration, data);
      return data;
    },

    onSuccess: (data) => {
      message.success('Project created successfully!');
      devLog.state('Projects', 'Project created', { projectId: data.id });
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    },

    onError: (error: Error) => {
      devLog.error('Projects', 'Failed to create project', {
        error: error.message,
        action: 'CREATE_PROJECT'
      });

      message.error({
        content: `Failed to create project: ${error.message}`,
        duration: 7,
      });
    },
  });
}
```

---

## Best Practices

### ✅ DO

1. **Always log errors with context**
   ```typescript
   devLog.error('FeatureName', 'What failed', {
     relevant: 'context',
     ids: ['ds-123', 'proj-456'],
     params: { /* request params */ }
   });
   ```

2. **Log user actions for debugging flows**
   ```typescript
   devLog.action('FeatureName', 'User clicked Button', { buttonId: 'submit' });
   ```

3. **Log state changes after mutations**
   ```typescript
   devLog.state('FeatureName', 'State updated', { newState });
   ```

4. **Use correlation for multi-step flows**
   ```typescript
   // devLog.action() starts correlation automatically
   devLog.action('Upload', 'User started upload', { fileName });
   // All subsequent logs will share correlationId
   ```

5. **Include stack traces for errors**
   ```typescript
   devLog.error('FeatureName', error.message, {
     error: error.message,
     stack: error.stack,
     context: { /* additional data */ }
   });
   ```

### ❌ DON'T

1. **Don't log sensitive data**
   ```typescript
   // BAD
   devLog.info('Auth', 'Login', { password: 'secret123' });

   // GOOD
   devLog.info('Auth', 'Login', { username: 'user@example.com' });
   ```

2. **Don't log without context**
   ```typescript
   // BAD
   devLog.error('Error', 'Failed');

   // GOOD
   devLog.error('DatasetUpload', 'Upload failed', {
     datasetId: 'ds-123',
     fileName: 'events.csv',
     fileSize: 1024000,
     error: 'Network timeout'
   });
   ```

3. **Don't spam logs in loops**
   ```typescript
   // BAD
   items.forEach(item => {
     devLog.info('Processing', item.id); // 1000 logs!
   });

   // GOOD
   devLog.info('Processing', `Processing ${items.length} items`, {
     itemIds: items.map(i => i.id).slice(0, 10) // First 10
   });
   ```

4. **Don't use console.log directly**
   ```typescript
   // BAD
   console.log('User clicked button');

   // GOOD
   devLog.action('FeatureName', 'User clicked button', { buttonId });
   ```

---

## Implementation Examples

### Example 1: Form Submission with Comprehensive Logging

```typescript
import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Form, Input, Button, message } from 'antd';
import { devLog } from '@/shared/ui';

function CreateProjectForm() {
  const [form] = Form.useForm();

  const createMutation = useMutation({
    mutationFn: async (values) => {
      devLog.action('ProjectForm', 'User submitted create form', {
        projectName: values.name,
        hasDescription: !!values.description
      });

      devLog.apiRequest('POST', '/api/v1/projects', values);
      const start = Date.now();

      const response = await fetch('/api/v1/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });

      const duration = Date.now() - start;
      const data = await response.json();

      if (!response.ok) {
        devLog.apiResponse('POST', '/api/v1/projects', response.status, duration, data);

        if (response.status === 400) {
          // Validation error
          devLog.info('ProjectForm', 'Validation failed', {
            validationErrors: data.errors
          });
          throw new Error('Validation failed');
        }

        throw new Error(data.message || 'Server error');
      }

      devLog.apiResponse('POST', '/api/v1/projects', 201, duration, data);
      devLog.state('ProjectForm', 'Project created successfully', {
        projectId: data.id,
        projectName: data.name
      });

      return data;
    },

    onError: (error) => {
      devLog.error('ProjectForm', 'Mutation failed', {
        error: error.message,
        formValues: form.getFieldsValue()
      });

      message.error(`Failed to create project: ${error.message}`);
    },

    onSuccess: (data) => {
      message.success('Project created successfully!');
      form.resetFields();
      devLog.action('ProjectForm', 'Form reset after success', {
        createdProjectId: data.id
      });
    }
  });

  return (
    <Form form={form} onFinish={createMutation.mutate}>
      <Form.Item name="name" rules={[{ required: true }]}>
        <Input placeholder="Project Name" />
      </Form.Item>
      <Form.Item name="description">
        <Input.TextArea placeholder="Description" />
      </Form.Item>
      <Button
        type="primary"
        htmlType="submit"
        loading={createMutation.isPending}
      >
        Create Project
      </Button>
    </Form>
  );
}
```

### Example 2: Data Fetching with Error Recovery

```typescript
import { useQuery } from '@tanstack/react-query';
import { Button, Alert } from 'antd';
import { devLog, LoadingState } from '@/shared/ui';

function DatasetList() {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['datasets'],
    queryFn: async () => {
      devLog.apiRequest('GET', '/api/v1/datasets');
      const start = Date.now();

      try {
        const response = await fetch('/api/v1/datasets');
        const duration = Date.now() - start;

        if (!response.ok) {
          const errorData = await response.json();
          devLog.apiResponse('GET', '/api/v1/datasets', response.status, duration, errorData);
          throw new Error(errorData.message || 'Failed to fetch');
        }

        const data = await response.json();
        devLog.apiResponse('GET', '/api/v1/datasets', 200, duration, {
          count: data.length
        });
        devLog.state('DatasetList', 'Datasets loaded', {
          count: data.length,
          datasetIds: data.map(d => d.id).slice(0, 5)
        });

        return data;
      } catch (error) {
        devLog.error('DatasetList', 'Failed to load datasets', {
          error: error.message,
          duration: Date.now() - start
        });
        throw error;
      }
    },
    retry: 3,
    retryDelay: (attempt) => Math.min(1000 * 2 ** attempt, 10000),
  });

  const handleRetry = () => {
    devLog.action('DatasetList', 'User clicked retry', {
      previousError: error?.message
    });
    refetch();
  };

  if (isLoading) {
    return <LoadingState type="skeleton" rows={5} />;
  }

  if (error) {
    return (
      <Alert
        type="error"
        message="Failed to load datasets"
        description={error.message}
        action={
          <Button size="small" type="primary" onClick={handleRetry}>
            Retry
          </Button>
        }
      />
    );
  }

  return (
    <div>
      {data.map(dataset => (
        <div key={dataset.id}>{dataset.name}</div>
      ))}
    </div>
  );
}
```

---

## Summary

- **4 error types**: Transient, Validation, Authorization, Critical
- **Feature-level error boundaries** in all 7 features
- **Intelligent logging** with importance scoring (1-5)
- **DevConsole integration** for debugging and development
- **Consistent notifications**: Toast, inline, modal, or error screen
- **Request correlation** for tracking multi-step user flows
- **Automatic retry** for transient network errors
- **Comprehensive context** in all logs for easy debugging

**Next Steps:**
1. Review and adopt logging patterns in new features
2. Use `devLog.action()` for all user interactions
3. Log state changes after mutations with `devLog.state()`
4. Check DevConsole in development for debugging flows
5. Export logs when reporting bugs (Export button in DevConsole)

