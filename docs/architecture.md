# Architecture

## System Overview

```mermaid
flowchart TB
    User[User Clients] --> Sup[Supervisor Agent]
    Sup --> LeafA[Leaf A Onboarding]
    Sup --> LeafB[Leaf B Diagnostics]
    Sup --> LeafC[Leaf C Retention]
    LeafA --> MCP[MCP Server]
    LeafB --> MCP
    LeafC --> MCP
    MCP --> CRM[Mock CRM]
    MCP --> Bill[Mock Billing]
    MCP --> Diag[Mock Diagnostics]
    Sup --> Mem[Memory API]
    LeafA --> Mem
    LeafB --> Mem
    LeafC --> Mem
```

## Supervisor → Leaf → MCP Sequence

```mermaid
sequenceDiagram
    participant U as User
    participant S as Supervisor
    participant L as Leaf B
    participant M as MCP
    participant D as Diagnostics

    U->>S: Message + session_id
    S->>S: Classify intent
    S->>L: invoke_agent
    L->>M: auth/exchange
    M-->>L: scoped token
    L->>M: call diagnostics.run
    M->>D: route request
    D-->>M: report
    M-->>L: structured output
    L->>Mem: write diag artifact
    L-->>S: summary
    S-->>U: merged response
```

## Memory Schema

| Scope | ID Pattern | Key Fields |
|-------|------------|------------|
| session | `session:<id>` | turns[], redaction_mask, consent |
| profile | `user:<id>` | company, plan, churn_score |
| diagnostic | `diag:<id>` | integration_id, checks[], status |
| aggregate | agent aggregates | churn_score, repeated_issues |

## CI/CD Pipeline

```mermaid
flowchart LR
    Lint --> Unit --> Integration --> Build
    Build --> Staging --> E2E --> Eval
    Eval --> Canary --> Production
```
