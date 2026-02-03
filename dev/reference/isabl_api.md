# isabl_api - Django REST API

> **Single source of truth** for the Isabl data model and API schema.

**Source**: `papaemmelab/isabl_api` (private)
**Framework**: Django REST Framework
**Database**: PostgreSQL

## Data Model Overview

```
Individual (patient/subject)
    └── Sample (tissue/blood)
        └── Aliquot (lab extraction)
            └── Experiment (sequencing run)
                    └── Analysis (pipeline execution)
                            └── Results (output files)
```

## Core Models

### Hierarchy Models

| Model | Description | Key Fields |
|-------|-------------|------------|
| **Individual** | Patient or subject | `system_id`, `identifier`, `species`, `gender`, `birth_year`, `center` |
| **Sample** | Biological specimen | `system_id`, `identifier`, `category`, `individual`, `disease` |
| **Aliquot** | Lab extraction from sample | `system_id`, `identifier`, `sample` |
| **Experiment** | Sequencing data | `system_id`, `sample`, `technique`, `platform`, `center`, `projects`, `raw_data`, `bam_files` |
| **Analysis** | Pipeline execution | `status`, `application`, `targets`, `references`, `results`, `storage_url` |

### Reference Models

| Model | Description | Key Fields |
|-------|-------------|------------|
| **Project** | Grouping for experiments | `title`, `short_title`, `principal_investigator`, `analyst`, `sharing` |
| **Application** | Registered pipeline | `name`, `version`, `assembly`, `results` (schema) |
| **Technique** | Sequencing method | `name`, `method`, `category`, `reference_data` |
| **Assembly** | Reference genome | `name`, `species`, `reference_data` |
| **Disease** | Disease classification | `name`, `acronym`, `slug` |
| **Center** | Institution | `name`, `acronym`, `slug` |
| **Platform** | Sequencing platform | `name`, `slug` |
| **Group** | Project grouping | `name`, `slug` |

## API Endpoints

Base URL: `/api/v1/`

### Standard CRUD Endpoints

All models have list and detail endpoints:

| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/analyses` | GET, POST | List/create analyses |
| `/analyses/<id>` | GET, PUT, PATCH, DELETE | Retrieve/update/delete analysis |
| `/experiments` | GET, POST | List/create experiments |
| `/experiments/<id>` | GET, PUT, PATCH, DELETE | Retrieve/update/delete experiment |
| `/projects` | GET, POST | List/create projects |
| `/samples` | GET, POST | List/create samples |
| `/individuals` | GET, POST | List/create individuals |
| `/applications` | GET, POST | List/create applications |

### Special Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/individuals/tree/<id>` | GET | Get individual with nested samples and experiments |
| `/individuals/tree` | GET | List individuals with hierarchy |
| `/analyses/bulk_update/` | POST | Bulk update analysis status |
| `/analyses/download/<pk>` | GET | Download analysis result file |
| `/analyses/stream/<pk>` | GET | Stream analysis result file |
| `/analyses/raw/<pk>` | GET | Read analysis result content |
| `/system_id/<system_id>` | GET | Redirect to instance by system_id |
| `/auth/` | POST | Get authentication token |
| `/preferences/` | GET, PUT | User preferences |

## Query Syntax

### Advanced Lookups

All fields support Django-style lookups:

| Lookup | Description | Example |
|--------|-------------|---------|
| `!` | Negate | `status!=FAILED` |
| `__exact` | Exact match | `name__exact=MUTECT` |
| `__iexact` | Case-insensitive exact | `name__iexact=mutect` |
| `__contains` | Contains substring | `name__contains=mut` |
| `__icontains` | Case-insensitive contains | `name__icontains=MUT` |
| `__startswith` | Starts with | `name__startswith=MU` |
| `__endswith` | Ends with | `name__endswith=CT` |
| `__in` | In list (comma-separated) | `status__in=FAILED,SUCCEEDED` |
| `__isnull` | Is null | `finished__isnull=true` |
| `__gt` | Greater than | `run_time__gt=60` |
| `__gte` | Greater or equal | `run_time__gte=60` |
| `__lt` | Less than | `run_time__lt=60` |
| `__lte` | Less than or equal | `run_time__lte=60` |
| `__regex` | Regex match | `name__regex=^MU.*CT$` |

### Datetime Lookups

| Lookup | Description | Example |
|--------|-------------|---------|
| `__date` | Filter by date | `created__date=2024-01-15` |
| `__date__gt` | After date | `created__date__gt=2024-01-01` |
| `__year` | Filter by year | `created__year=2024` |
| `__month` | Filter by month | `created__month=6` |

### Relational Lookups

Traverse relationships with `__`:

```
# Experiments by project
/experiments?projects__pk=102

# Analyses by application name
/analyses?application__name=MUTECT

# Experiments by technique method
/experiments?technique__method=WGS

# Analyses by target project
/analyses?targets__projects__pk=102
```

### Response Field Selection

Use `fields` parameter to limit returned fields:

```
/experiments?fields=pk,system_id,technique
/analyses?fields=pk,status,application__name
```

Use `fields` with nested syntax for related fields:

```
/experiments?fields=pk,sample__system_id,sample__individual__system_id
```

## Analysis Status Values

| Status | Description |
|--------|-------------|
| `CREATED` | Analysis record created, not yet staged |
| `STAGED` | Ready to run, CLI has validated inputs |
| `SUBMITTED` | Submitted to job scheduler |
| `STARTED` | Running on compute |
| `SUCCEEDED` | Completed successfully |
| `FAILED` | Failed with error |
| `IN_PROGRESS` | Long-running, still producing output |
| `FINISHED` | Completed (alternate to SUCCEEDED) |
| `REJECTED` | Rejected by user/admin |

## Key Field Details

### Analysis Model

```python
class Analysis:
    # Relationships
    application: Application      # The pipeline being run
    targets: [Experiment]         # Input experiments (tumor, sample)
    references: [Experiment]      # Reference experiments (normal, control)
    analyses: [Analysis]          # Linked analyses (dependencies)
    project_level_analysis: Project  # If project-level (no targets)
    individual_level_analysis: Individual  # If individual-level

    # Status tracking
    status: str                   # CREATED, STAGED, SUBMITTED, STARTED, SUCCEEDED, FAILED
    previous_status: str          # Status before current
    submitted: datetime           # When submitted
    started: datetime             # When started running
    finished: datetime            # When completed
    run_time: float               # Minutes running
    wait_time: float              # Minutes in queue

    # Results
    results: dict                 # Output files and data
    storage_url: str              # Path to output directory
    storage_usage: int            # Bytes used

    # Metadata
    ran_by: User                  # Who ran it
    created_by: User              # Who created it
    data: dict                    # Arbitrary JSON
    custom_fields: dict           # Structured custom fields
    tags: [Tag]                   # Tags for organization
```

### Experiment Model

```python
class Experiment:
    # Relationships
    sample: Sample                # Parent sample
    aliquot: Aliquot              # Lab aliquot
    technique: Technique          # Sequencing method
    platform: Platform            # Sequencing platform
    center: Center                # Where sequenced
    projects: [Project]           # Project memberships

    # Data
    system_id: str                # Auto-generated ID (e.g., "ISB_H000001_T01_WGS01")
    identifier: str               # External identifier
    raw_data: [dict]              # FASTQ/BAM paths with metadata
    bam_files: dict               # Default BAMs by assembly
    results: [dict]               # Cached analysis results

    # Metadata
    storage_url: str
    storage_usage: int
    data: dict
    custom_fields: dict
    tags: [Tag]
```

### Sample Category Values

| Category | Description |
|----------|-------------|
| `TUMOR` | Tumor tissue |
| `NORMAL` | Normal tissue |
| `GERMLINE` | Germline sample |
| `METASTASIS` | Metastatic tissue |
| `RELAPSE` | Relapse sample |
| `PRIMARY` | Primary tumor |
| `XENOGRAFT` | PDX sample |
| `UNKNOWN` | Unknown category |

### Technique Method Values

Common values (configurable per installation):

| Method | Description |
|--------|-------------|
| `WGS` | Whole Genome Sequencing |
| `WES` | Whole Exome Sequencing |
| `RNA` | RNA Sequencing |
| `PANEL` | Targeted Panel |
| `SC_DNA` | Single-cell DNA |
| `SC_RNA` | Single-cell RNA |
| `ONT` | Oxford Nanopore |
| `ATAC` | ATAC-seq |

## Authentication

### Token Authentication

```bash
# Get token
curl -X POST /api/v1/auth/ \
  -d '{"username": "user", "password": "pass"}'
# Returns: {"key": "TOKEN"}

# Use token
curl -H "Authorization: Token TOKEN" /api/v1/experiments/
```

### Session Authentication

Browser-based using Django sessions.

## Pagination

Default: 100 items per page

```
/experiments?limit=50&offset=100
```

Response includes:
```json
{
  "count": 1234,
  "next": "/api/v1/experiments?limit=50&offset=150",
  "previous": "/api/v1/experiments?limit=50&offset=50",
  "results": [...]
}
```

## Ordering

```
/analyses?ordering=-created           # Descending by created
/analyses?ordering=run_time           # Ascending by run_time
/analyses?ordering=application__name  # By related field
```

## Common Query Patterns

### Get failed analyses for a project
```
/analyses?targets__projects__pk=102&status=FAILED
```

### Get experiments by technique
```
/experiments?technique__method=WGS&projects__pk=102
```

### Get analyses for an individual
```
/analyses?targets__sample__individual__pk=500
```

### Get recent analyses
```
/analyses?created__date__gte=2024-01-01&ordering=-created
```

### Get analyses by application
```
/analyses?application__name=MUTECT&status=SUCCEEDED
```

### Get individual tree with all descendants
```
/individuals/tree/123
```

## Storage URL Conventions

Analysis results are stored at `storage_url`:

```
{storage_url}/
├── head_job.log      # Main job log (stdout)
├── head_job.err      # Error log (stderr)
├── head_job.sh       # Job script
├── {result_key}.ext  # Result files defined in application.results
└── ...
```

## Results Schema

The `results` field on Analysis matches the schema defined in `application.results`:

```json
{
  "result_key": {
    "frontend_type": "table|igv|plot|...",
    "verbose_name": "Human readable name",
    "description": "What this result contains",
    "optional": false,
    "data": {}
  }
}
```

Common result keys: `vcf`, `bam`, `tsv`, `summary`, `qc_metrics`

## Custom Fields

Models supporting custom fields: Individual, Sample, Experiment, Analysis

Query custom fields directly:

```
/experiments?is_pdx=true
/analyses?tumor_purity__gte=0.5
```

## Project Sharing

Projects have a `sharing` field:

```json
{
  "is_public": false,
  "can_read": ["user1@example.com", "user2@example.com"],
  "can_share": ["admin@example.com"]
}
```
