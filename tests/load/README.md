# Load Testing

Skeleton for load testing with k6 or Locust.

## k6 example

```javascript
import http from 'k6/http';
import { check } from 'k6';

export const options = { vus: 100, duration: '5m' };

export default function () {
  const res = http.post('http://localhost:8020/runtime/session/call_model', JSON.stringify({
    session_id: 'load-test',
    user_input: 'help with onboarding',
  }), { headers: { 'Content-Type': 'application/json' } });
  check(res, { 'status is 200': (r) => r.status === 200 });
}
```

Target: 10k concurrent sessions with median latency < 1.5s.
