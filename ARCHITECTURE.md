# ETL Pipeline Architecture

This document provides visual architecture diagrams for the Salesforce to Supabase ETL pipeline, designed for executive and technical presentations.

---

## Executive Summary Diagram

```mermaid
flowchart TB
    subgraph "Data Sources"
        SF[Salesforce CSV Exports<br/>Daily Reports]
    end
    
    subgraph "Entry Points"
        Email[CloudMailin Webhook<br/>Automated 6 AM Daily]
        Manual[Web Upload Interface<br/>Manual/Backfill]
    end
    
    subgraph "ETL Pipeline"
        QA[Quality Validation<br/>✓ Headers<br/>✓ Duplicates<br/>✓ Required Fields]
        Transform[Data Transformation<br/>YAML-Driven Rules<br/>• Rename Columns<br/>• Type Conversion<br/>• Date Formatting]
        Load[Bulk Load<br/>PostgreSQL COPY<br/>High Performance]
    end
    
    subgraph "Data Warehouse"
        DB[(Supabase PostgreSQL<br/>7 Staging Tables<br/>Analytics Ready)]
    end
    
    subgraph "Monitoring & Analytics"
        Dashboard[Web Dashboards<br/>Load History<br/>Webhook Activity<br/>Real-time Progress]
        Alerts[Notifications<br/>Success/Failure Alerts<br/>Logged to File]
        Analytics[Analytics & BI Tools<br/>Query Staging Tables<br/>Business Reports]
    end
    
    subgraph "Error Handling"
        Quarantine[Quarantine System<br/>Failed Files + Logs]
    end
    
    SF --> Email
    SF --> Manual
    
    Email --> QA
    Manual --> QA
    
    QA -->|Pass| Transform
    QA -->|Fail| Quarantine
    
    Transform --> Load
    Load --> DB
    
    DB --> Analytics
    
    Load --> Dashboard
    Load --> Alerts
    Quarantine --> Dashboard
    Quarantine --> Alerts
    
    style SF fill:#e1f5ff
    style Email fill:#b8e6b8
    style Manual fill:#fff4b8
    style QA fill:#ffd4b8
    style Transform fill:#ffd4b8
    style Load fill:#ffd4b8
    style DB fill:#d4b8ff
    style Dashboard fill:#e8e8e8
    style Alerts fill:#ffffcc
    style Analytics fill:#c8e6c9
    style Quarantine fill:#ffb8b8
```

**Key Benefits:**
- 🚀 **Automated**: Daily processing via email webhook (eliminates manual work)
- ✅ **Reliable**: Quality validation prevents bad data from entering warehouse
- ⚡ **Fast**: Bulk PostgreSQL COPY loads 600K+ rows in seconds
- 🛡️ **Safe**: Quarantine system isolates failures without blocking good data

---

## Detailed Technical Architecture

```mermaid
flowchart TB
    subgraph "External Systems"
        SF[Salesforce<br/>Daily CSV Exports]
        CloudMailin[CloudMailin Service<br/>Email-to-Webhook]
    end
    
    subgraph "Entry Layer"
        Webhook["/webhook/cloudmailin<br/>Token Auth + HTTPS"]
        Upload["/upload<br/>Web Interface<br/>100 MB Limit"]
    end
    
    subgraph "Flask Application Layer"
        direction TB
        Router[Flask Router<br/>main.py]
        Progress[Real-time Progress<br/>AJAX Polling]
    end
    
    subgraph "ETL Core Modules"
        direction TB
        Mapper[Mapping Parser<br/>etl/mapper.py<br/>YAML Rules]
        Validator[QA Validator<br/>etl/validator.py<br/>Header/Duplicate Check]
        Transformer[Data Transformer<br/>etl/transformer.py<br/>Column Rename/Coerce]
        Loader[Bulk Loader<br/>etl/loader.py<br/>PostgreSQL COPY<br/>UPSERT/INSERT Strategy]
        Notifier[Notification Service<br/>etl/notifications.py<br/>Success/Failure Alerts]
    end
    
    subgraph "Data Storage"
        direction LR
        Staging[(Staging Tables<br/>contacts<br/>job_applicant<br/>form_submission<br/>jobs_and_placements<br/>contacts_with_jobs<br/>job_applicant_history<br/>placement_history)]
        
        Metadata[(Metadata Tables<br/>load_history<br/>webhook_log)]
        
        Quarantine[("Quarantine Storage<br/>quarantine/<br/>Failed Files")]
    end
    
    subgraph "Observability & Consumption"
        direction TB
        Dashboards[Web Dashboards<br/>• Load History<br/>• Webhook Activity<br/>• Real-time Progress]
        Analytics[Analytics & BI<br/>• Tableau/PowerBI<br/>• SQL Queries<br/>• Business Reports]
    end
    
    subgraph "Configuration"
        YAML[YAML Mappings<br/>Mappings/*.yaml<br/>Field Rules<br/>Natural Keys<br/>Transformations]
    end
    
    SF --> CloudMailin
    CloudMailin --> Webhook
    SF -.Manual.-> Upload
    
    Webhook --> Router
    Upload --> Router
    
    Router --> Progress
    Router --> Mapper
    
    YAML --> Mapper
    Mapper --> Validator
    
    Validator -->|Pass| Transformer
    Validator -->|Fail| Quarantine
    
    Transformer --> Loader
    
    Loader -->|UPSERT Mode<br/>Natural Key Match| Staging
    Loader -->|INSERT Mode<br/>History Tables| Staging
    
    Loader --> Metadata
    Loader --> Notifier
    Validator --> Metadata
    Quarantine --> Notifier
    
    Progress -.Polls Status.-> Metadata
    
    Metadata --> Dashboards
    Staging --> Analytics
    
    style SF fill:#e1f5ff
    style CloudMailin fill:#e1f5ff
    style Webhook fill:#b8e6b8
    style Upload fill:#fff4b8
    style Router fill:#ffd4b8
    style Mapper fill:#ffd4b8
    style Validator fill:#ffd4b8
    style Transformer fill:#ffd4b8
    style Loader fill:#ffd4b8
    style Notifier fill:#ffffcc
    style Staging fill:#d4b8ff
    style Metadata fill:#e8e8e8
    style Quarantine fill:#ffb8b8
    style Dashboards fill:#e8e8e8
    style Analytics fill:#c8e6c9
    style YAML fill:#ffffcc
    style Progress fill:#b8e6b8
```

---

## Data Flow Sequence Diagram

```mermaid
sequenceDiagram
    participant SF as Salesforce
    participant CM as CloudMailin
    participant Flask as Flask App
    participant Val as Validator
    participant Trans as Transformer
    participant Load as Loader
    participant DB as PostgreSQL
    participant Notify as Notifications
    participant Q as Quarantine
    
    SF->>CM: Daily CSV Export (6 AM)
    CM->>Flask: POST /webhook/cloudmailin
    activate Flask
    
    Flask->>Flask: Verify Token Auth
    Flask->>Flask: Auto-detect YAML Mapping (from filename)
    Flask->>DB: Create load_history Record
    
    Flask->>Val: Validate CSV
    activate Val
    
    Val->>Val: Check Headers
    Val->>Val: Detect Duplicates
    Val->>Val: Verify Required Fields
    
    alt Validation Passes
        Val-->>Flask: ✓ Valid
        deactivate Val
        
        Flask->>Trans: Transform Data
        activate Trans
        Trans->>Trans: Apply YAML Rules
        Trans->>Trans: Rename Headers
        Trans->>Trans: Coerce Types
        Trans-->>Flask: Transformed CSV
        deactivate Trans
        
        Flask->>Load: Bulk Load
        activate Load
        
        alt UPSERT Mode (Natural Key)
            Load->>DB: CREATE TEMP TABLE
            Load->>DB: COPY to Temp
            Load->>DB: DELETE Old Records
            Load->>DB: INSERT New Records
        else INSERT Mode (History)
            Load->>DB: COPY Direct Insert
        end
        
        Load-->>Flask: Success (Row Count)
        deactivate Load
        
        Flask->>DB: Update load_history (success)
        Flask->>Notify: Log Success (file, rows, table)
        Flask-->>CM: 200 OK
        
    else Validation Fails
        Val-->>Flask: ✗ Errors
        deactivate Val
        Flask->>Q: Move to Quarantine
        Flask->>DB: Update load_history (failed)
        Flask->>Notify: Log Failure (file, errors, quarantine path)
        Flask-->>CM: 200 OK (quarantined)
    end
    
    deactivate Flask
```

---

## Security Architecture

```mermaid
flowchart LR
    subgraph "Security Layers"
        direction TB
        
        Auth[Token Authentication<br/>CLOUDMAILIN_WEBHOOK_TOKEN<br/>HTTP Basic Auth]
        
        HTTPS[HTTPS-Only Downloads<br/>Domain Allowlist<br/>S3/GCS/Azure/CloudMailin]
        
        SQL[SQL Injection Protection<br/>psycopg2.sql.Identifier<br/>Table Allowlist<br/>Named Parameters]
        
        Size[Size Limits<br/>100 MB Upload<br/>30s Timeout]
        
        Validate[Input Validation<br/>CSV Headers<br/>File Type Check<br/>Required Fields]
    end
    
    subgraph "Attack Prevention"
        SSRF[SSRF Prevention<br/>Hostname Validation]
        Inject[SQL Injection<br/>Parameterized Queries]
        DOS[DoS Protection<br/>Size + Timeout Limits]
    end
    
    Auth --> SSRF
    HTTPS --> SSRF
    SQL --> Inject
    Size --> DOS
    Validate --> Inject
    
    style Auth fill:#b8e6b8
    style HTTPS fill:#b8e6b8
    style SQL fill:#b8e6b8
    style Size fill:#b8e6b8
    style Validate fill:#b8e6b8
    style SSRF fill:#ffd4b8
    style Inject fill:#ffd4b8
    style DOS fill:#ffd4b8
```

---

## Load Strategy: UPSERT vs INSERT Mode

```mermaid
flowchart TB
    subgraph "Load Decision"
        Start[New CSV File]
        Check{Natural Key<br/>Defined?}
    end
    
    subgraph "UPSERT Mode"
        direction TB
        U1[Create Temp Table]
        U2[COPY CSV to Temp]
        U3[DELETE FROM target<br/>WHERE natural_key IN temp]
        U4[INSERT FROM temp]
        U5[Result: Latest Data Only]
    end
    
    subgraph "INSERT Mode"
        direction TB
        I1[Direct COPY to Table]
        I2[Result: All Events Preserved]
    end
    
    subgraph "Tables by Mode"
        direction LR
        UPSERT_Tables["UPSERT Tables:<br/>✓ contacts<br/>✓ job_applicant<br/>✓ form_submission<br/>✓ jobs_and_placements<br/>✓ contacts_with_jobs"]
        
        INSERT_Tables["INSERT Tables:<br/>✓ job_applicant_history<br/>✓ placement_history"]
    end
    
    Start --> Check
    Check -->|Yes<br/>Master Data| U1
    Check -->|No<br/>History/Events| I1
    
    U1 --> U2 --> U3 --> U4 --> U5
    I1 --> I2
    
    U5 -.Example.-> UPSERT_Tables
    I2 -.Example.-> INSERT_Tables
    
    style Start fill:#e8e8e8
    style Check fill:#fff4b8
    style U1 fill:#d4b8ff
    style U2 fill:#d4b8ff
    style U3 fill:#d4b8ff
    style U4 fill:#d4b8ff
    style U5 fill:#b8e6b8
    style I1 fill:#d4b8ff
    style I2 fill:#b8e6b8
    style UPSERT_Tables fill:#ffffcc
    style INSERT_Tables fill:#ffffcc
```

---

## System Components Overview

### Entry Points
- **CloudMailin Webhook**: Automated daily processing via email (6 AM scheduled)
- **Web Upload Interface**: Manual uploads and historical backfills

### ETL Pipeline Modules
- **Mapping Parser** (`etl/mapper.py`): Loads YAML transformation rules
- **QA Validator** (`etl/validator.py`): Header, duplicate, and required field validation
- **Data Transformer** (`etl/transformer.py`): Column renaming and type coercion
- **Bulk Loader** (`etl/loader.py`): High-performance PostgreSQL COPY operations

### Data Storage
- **7 Staging Tables**: Salesforce data optimized for analytics
- **Metadata Tables**: `load_history` (ETL runs), `webhook_log` (automation tracking)
- **Quarantine System**: Failed file isolation with error logging

### Configuration
- **YAML Mappings** (`Mappings/*.yaml`): Define field transformations, natural keys, and load strategies
- **Environment Variables**: Database connections, webhook tokens

### Monitoring
- **Real-time Progress Tracking**: AJAX polling with visual progress bar
- **Load History Dashboard**: Success/failure tracking with row counts and timing
- **Webhook Activity Log**: Email processing monitoring

---

## Performance Characteristics

| Metric | Value |
|--------|-------|
| **Bulk Load Speed** | 600K+ rows in seconds (PostgreSQL COPY) |
| **Validation Performance** | Single-pass algorithm, 50K row progress updates |
| **File Size Limit** | 100 MB per upload |
| **Encoding Support** | UTF-8, Windows-1252, ISO-8859-1 (graceful handling) |
| **UPSERT Strategy** | Temp table approach (no schema locks) |
| **Concurrency** | Connection retry logic with keep-alive |

---

## Error Handling & Resilience

```mermaid
flowchart LR
    subgraph "Error Detection"
        E1[Validation Errors]
        E2[Transformation Errors]
        E3[Load Errors]
        E4[Connection Errors]
    end
    
    subgraph "Recovery Actions"
        R1[Quarantine File<br/>+ Error Log]
        R2[Update load_history<br/>Status: Failed]
        R3[Retry Connection<br/>5 attempts<br/>Exponential Backoff]
        R4[Notification Log<br/>etl_notifications.log]
    end
    
    E1 --> R1
    E2 --> R1
    E3 --> R1
    E1 --> R2
    E2 --> R2
    E3 --> R2
    E4 --> R3
    
    R1 --> R4
    R2 --> R4
    
    style E1 fill:#ffb8b8
    style E2 fill:#ffb8b8
    style E3 fill:#ffb8b8
    style E4 fill:#ffb8b8
    style R1 fill:#ffd4b8
    style R2 fill:#ffd4b8
    style R3 fill:#b8e6b8
    style R4 fill:#e8e8e8
```

---

## Deployment Architecture

```mermaid
flowchart TB
    subgraph "Production Environment"
        LB[Load Balancer<br/>Autoscale]
        
        subgraph "Flask Instances"
            F1[Gunicorn Worker 1]
            F2[Gunicorn Worker 2]
            F3[Gunicorn Worker N]
        end
        
        Cache[Static Assets<br/>CSS/JS]
    end
    
    subgraph "External Services"
        CM[CloudMailin<br/>Email Processing]
        Supabase[(Supabase PostgreSQL<br/>Managed Database<br/>Connection Pooling)]
    end
    
    subgraph "Storage"
        FS[Temporary File Storage<br/>uploads/<br/>quarantine/]
    end
    
    CM --> LB
    LB --> F1
    LB --> F2
    LB --> F3
    
    F1 --> Supabase
    F2 --> Supabase
    F3 --> Supabase
    
    F1 --> FS
    F2 --> FS
    F3 --> FS
    
    LB --> Cache
    
    style LB fill:#b8e6b8
    style F1 fill:#ffd4b8
    style F2 fill:#ffd4b8
    style F3 fill:#ffd4b8
    style CM fill:#e1f5ff
    style Supabase fill:#d4b8ff
    style FS fill:#e8e8e8
    style Cache fill:#ffffcc
```

---

## Usage Instructions

### For Presentations

1. **Executive Summary Diagram**: Perfect for CEO/CFO - shows business value and automation
2. **Detailed Technical Architecture**: For CTO - shows all components and data flow
3. **Security Architecture**: Highlights protection mechanisms
4. **Load Strategy Diagram**: Explains UPSERT vs INSERT logic

### Viewing Options

- **GitHub/Markdown Viewers**: Diagrams render automatically
- **Mermaid Live Editor**: Copy/paste into https://mermaid.live for editing
- **Export as Images**: Use Mermaid Live Editor to export PNG/SVG for PowerPoint
- **Documentation**: Embed in Confluence, Notion, or other docs platforms

### Customization

Edit the Mermaid code blocks to:
- Adjust colors (e.g., `fill:#color`)
- Add/remove components
- Change layout direction (`TB` = top-to-bottom, `LR` = left-to-right)
- Modify text and labels
