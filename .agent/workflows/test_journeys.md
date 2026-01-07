---
description: Run E2E user journey tests to simulate frontend flows
---

# Run User Journey Tests

// turbo-all

1. Ensure backend is running
```bash
curl -s http://localhost:8001/health | jq -r '.status'
```

2. Run all journey tests
```bash
cd /Users/namanagarwal/system/test/e2e && python -m pytest -v journeys/ --tb=short
```

3. Run specific journey (upload is most critical)
```bash
cd /Users/namanagarwal/system/test/e2e && python -m pytest -v journeys/test_journey_02_upload.py --tb=short
```

4. Run with debug output
```bash
cd /Users/namanagarwal/system/test/e2e && python -m pytest -v -s journeys/ --tb=long
```
