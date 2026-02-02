# Isabl CLI

> Command-line interface and Python SDK for the Isabl genomics platform

## Quick Reference

```python
import isabl_cli as ii

# Query experiments
experiments = ii.get_experiments(projects=102, sample__category="TUMOR")

# Get single instance
exp = ii.Experiment("SAMPLE_001")
analysis = ii.Analysis(12345)

# CRUD operations
ii.create_instance("analyses", application=123, targets=[exp1])
ii.patch_instance("analyses", pk, status="STARTED")
```

## Data Model

```
Individual → Sample → Experiment → Analysis
                           ↓
                       Project
```

| Entity | Description |
|--------|-------------|
| Individual | Patient or organism |
| Sample | Tissue or cell type from individual |
| Experiment | Sequencing run data (FASTQ/BAM) |
| Analysis | Processed result from an application |
| Application | Pipeline metadata (NAME, VERSION, ASSEMBLY) |

## Query Filters

| Operator | Example | Purpose |
|----------|---------|---------|
| `__contains` | `name__contains=tumor` | Substring match |
| `__in` | `status__in=SUCCEEDED,FAILED` | Multiple values |
| `__gt`, `__gte`, `__lt`, `__lte` | `created__gt=2024-01-01` | Comparison |
| `__isnull` | `results__isnull=false` | Null check |
| `!` prefix | `status!=FAILED` | Negation |

## Writing Applications

```python
from isabl_cli import AbstractApplication, options

class MyApp(AbstractApplication):
    NAME = "my_app"
    VERSION = "1.0.0"
    ASSEMBLY = "GRCh37"  # Optional
    SPECIES = "HUMAN"    # Optional

    cli_options = [options.TARGETS]

    application_settings = {
        "tool_path": "/usr/bin/tool",
    }

    def validate_experiments(self, targets, references):
        """Raise AssertionError if experiments are invalid."""
        assert len(targets) == 1, "Requires exactly one target"

    def get_command(self, analysis, inputs, settings):
        """Return shell command to execute."""
        return f"{settings.tool_path} {analysis.targets[0].bam}"

    def get_analysis_results(self, analysis):
        """Return dict of result paths after completion."""
        return {"output": f"{analysis.storage_url}/result.txt"}
```

## CLI Commands

```bash
# Authentication
isabl login

# Run application
isabl myapp-1-0 --targets EXP1 EXP2 --commit

# Query data
isabl get-results --application 123 --status SUCCEEDED
isabl get-bams --projects 102
isabl get-count --status FAILED

# Flags
--commit    # Actually submit (default: stage only)
--force     # Wipe incomplete and restart
--restart   # Resume from checkpoint
--local     # Execute locally instead of batch system
```

## Analysis Status Flow

```
CREATED → STAGED → SUBMITTED → STARTED → SUCCEEDED/FINISHED/FAILED
```

## Batch Systems

Supported: SLURM, LSF, SGE, local

Configure via `SUBMIT_ANALYSES` setting.

## Common Patterns

### Get results from an experiment
```python
from isabl_cli import utils
vcf = utils.get_result(
    experiment=exp,
    application_key=123,
    result_key="vcf"
)
```

### Traverse relationships
```python
for analysis in analyses:
    for target in analysis.targets:
        individual = target.sample.individual
        print(individual.identifier)
```

### Check if analysis exists
```python
existing = ii.get_analyses(
    application=app.pk,
    targets__pk=exp.pk,
    status__in=["SUCCEEDED", "STARTED"]
)
```

## Environment Variables

```bash
ISABL_API_URL="https://api.isabl.io/api/v1/"
ISABL_CLIENT_ID="cli"
```

## Project Conventions

- Use `ii` as the import alias for `isabl_cli`
- Applications inherit from `AbstractApplication`
- Results stored under `analysis.storage_url`
- Status changes trigger signals (ON_STATUS_CHANGE)
