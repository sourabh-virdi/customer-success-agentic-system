# Mocks

Mock backend services for local development and testing.

```bash
export PYTHONPATH=mocks
uvicorn mocks.crm.main:app --port 8010
uvicorn mocks.billing.main:app --port 8011
uvicorn mocks.diagnostics.main:app --port 8012
```

Test data: `mocks/test_data/`
