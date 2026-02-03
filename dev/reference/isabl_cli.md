# isabl_cli Analysis

> Command Line Client and Python SDK for the Isabl Platform

**Repository**: `papaemmelab/isabl_cli`
**Language**: Python 3.6+
**CLI Framework**: Click

## Purpose

isabl_cli is the primary interface for interacting with the Isabl platform. It provides:

- **CLI Interface**: Commands for launching analyses and managing data
- **Python SDK**: Library functions for programmatic API interaction
- **Analysis Framework**: Extensible architecture for writing custom bioinformatics applications
- **Batch System Integration**: Submit jobs to SLURM, LSF, SGE, or local execution

## Key Modules

| Module | Purpose |
|--------|---------|
| `api.py` | Core API client - authentication, HTTP requests, CRUD operations |
| `app.py` | AbstractApplication base class (~1600 lines) |
| `cli.py` | CLI entry point using Click |
| `commands.py` | Built-in system commands |
| `data.py` | Data import logic (~1100 lines) |
| `settings.py` | Configuration system |
| `batch_systems/` | SLURM, LSF, SGE, local submission adapters |

## Data Model

```
Individual (person) → Sample → Experiment → Analysis
                                    ↓
                               Project
```

- **Individual**: Patient/organism
- **Sample**: Tissue/cell type
- **Experiment**: Sequencing run (raw FASTQ/BAM)
- **Analysis**: Processed result (output of application)
- **Application**: Pipeline metadata (NAME, VERSION, ASSEMBLY)

## SDK Usage Patterns

### Basic API Usage

```python
from isabl_cli import api

# Retrieve instances
experiment = api.get_instance("experiments", "sample_001")
analyses = api.get_instances("analyses", application=123, status="SUCCEEDED")

# CRUD operations
new_analysis = api.create_instance("analyses", application=123, targets=[exp1])
api.patch_instance("analyses", pk, status="STARTED")

# Query with filters
experiments = api.get_experiments(projects=102, sample__category="TUMOR")
```

### Filter Operators

| Operator | Example | Purpose |
|----------|---------|---------|
| `!` | `name!=isabel` | Negation |
| `__contains` | `name__contains=isa` | Substring |
| `__in` | `name__in=a,b` | Multiple values |
| `__gt`, `__gte`, `__lt`, `__lte` | `total__gt=1` | Numeric comparison |
| `__isnull` | `name__isnull=true` | Null checks |

### Writing an Application

```python
from isabl_cli import AbstractApplication, options

class VariantCaller(AbstractApplication):
    NAME = "variant_caller"
    VERSION = "2.1.0"
    ASSEMBLY = "GRCh37"
    SPECIES = "HUMAN"

    cli_options = [options.TARGETS, options.REFERENCES]

    application_settings = {
        "samtools_path": "/usr/bin/samtools",
    }

    def validate_experiments(self, targets, references):
        for exp in targets:
            assert exp.technique.method in ["WG", "WE", "CS"]

    def get_command(self, analysis, inputs, settings):
        return f"{settings.samtools_path} ..."

    def get_analysis_results(self, analysis):
        return {"vcf": f"{analysis.storage_url}/output.vcf.gz"}
```

## CLI Commands

### System Commands

```bash
isabl login                          # Authenticate
isabl get-results [filters]          # Query analysis results
isabl get-bams [filters]             # Get BAM file paths
isabl patch-status --key PK --status STATUS
```

### Application Commands

```bash
# Structure: isabl <app-slug>-<version> [options]
isabl myapp-1-0 --targets EXP1 EXP2 --commit
isabl myapp-1-0 --pair TARGET REFERENCE --force
isabl myapp-1-0 --analyses [filters] --restart
```

**Flags:**
- `--commit`: Actually submit (default: stage only)
- `--force`: Wipe incomplete and restart
- `--restart`: Resume from checkpoint
- `--local`: Execute locally

## Configuration

### Environment Variables

```bash
ISABL_API_URL="http://localhost:8000/api/v1/"
ISABL_CLIENT_ID="cli-client"
ISABL_API_TOKEN  # Cached auth token
```

### Settings Module

```python
INSTALLED_APPLICATIONS = []  # AbstractApplication subclasses
SUBMIT_ANALYSES = "isabl_cli.batch_systems.submit_local"
BASE_STORAGE_DIRECTORY = "~/isabl_storage"
ON_STATUS_CHANGE = []  # Signal handlers
ON_DATA_IMPORT = []    # Signal handlers
```

## Analysis Lifecycle

```
CREATED → STAGED → SUBMITTED → STARTED → SUCCEEDED/FINISHED/FAILED
```

## Key Concepts for AI Agents

1. **Applications are metadata-driven**: They generate commands from database metadata, not hardcoded paths
2. **Infrastructure-agnostic**: Submitters handle different batch systems
3. **Signal-based automation**: Status changes trigger registered handlers
4. **Dependency resolution**: Applications can depend on results from other applications
5. **Result extraction**: `get_analysis_results()` structures outputs for database storage

## Storage Structure

```
BASE_STORAGE_DIRECTORY/
├── experiments/<exp_id>/
│   ├── analyses/      # Symlinks to analysis results
│   └── raw_data/      # FASTQ files
├── analyses/23/45/12345/
│   ├── head_job.sh    # Command script
│   ├── head_job.log   # stdout
│   ├── head_job.err   # stderr
│   └── output.vcf.gz  # Results
└── projects/<proj_id>/
    └── analyses/      # Symlinks
```
