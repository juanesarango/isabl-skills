---
name: isabl-query-data
description: Help construct queries to retrieve data from Isabl using the Python SDK. Use when searching for experiments, analyses, samples, or other data.
tools: Read, Bash
model: inherit
---

# Querying Isabl Data

You are helping the user query data from the Isabl platform using the Python SDK.

## Quick Reference

```python
import isabl_cli as ii

# Basic queries
experiments = ii.get_experiments(projects=102)
analyses = ii.get_analyses(application=123, status="SUCCEEDED")
samples = ii.get_instances("samples", individual__species="HUMAN")

# Single instance
exp = ii.Experiment("SAMPLE_001")  # by system_id
analysis = ii.Analysis(12345)       # by pk
```

## Query Patterns

### Filter Operators

| Operator | Example | Purpose |
|----------|---------|---------|
| (none) | `status="SUCCEEDED"` | Exact match |
| `__contains` | `name__contains="tumor"` | Substring |
| `__icontains` | `name__icontains="TUMOR"` | Case-insensitive substring |
| `__startswith` | `name__startswith="PT"` | Starts with |
| `__in` | `status__in=["SUCCEEDED","FAILED"]` | One of values |
| `__gt`, `__gte` | `created__gt="2024-01-01"` | Greater than |
| `__lt`, `__lte` | `total__lte=100` | Less than |
| `__isnull` | `results__isnull=False` | Is/isn't null |
| `!` prefix | `status!="FAILED"` | Negation |

### Traverse Relationships

Use double underscore to traverse:

```python
# Experiments in a specific project
ii.get_experiments(projects=102)

# Experiments for a specific individual
ii.get_experiments(sample__individual__pk=500)

# Analyses by application name
ii.get_analyses(application__name="variant_caller")

# Experiments with specific technique
ii.get_experiments(technique__method="WGS")
```

## Common Queries

### Find experiments by project

```python
experiments = ii.get_experiments(
    projects=102,
    sample__category="TUMOR"
)
for exp in experiments:
    print(f"{exp.system_id}: {exp.sample.identifier}")
```

### Find successful analyses for an application

```python
analyses = ii.get_analyses(
    application__name="variant_caller",
    application__version="2.0.0",
    status="SUCCEEDED"
)
for a in analyses:
    print(f"Analysis {a.pk}: {a.results}")
```

### Find failed analyses

```python
failed = ii.get_analyses(
    status="FAILED",
    created__gt="2024-01-01"
)
for a in failed:
    print(f"{a.pk}: {a.application.name}")
```

### Count records without fetching

```python
count = ii.get_instances_count("experiments", projects=102)
print(f"Total experiments: {count}")
```

### Get individual's full tree

```python
individual = ii.get_tree(individual_pk)
for sample in individual.sample_set:
    print(f"Sample: {sample.identifier}")
    for exp in sample.experiment_set:
        print(f"  Experiment: {exp.system_id}")
```

### Find experiments with specific raw data

```python
# Experiments that have raw data
experiments = ii.get_experiments(
    raw_data__isnull=False,
    technique__method="WGS"
)
```

### Get results from analyses

```python
from isabl_cli import utils

# Get specific result from an experiment
vcf_path, analysis = utils.get_result(
    experiment=experiment,
    application_key=123,
    result_key="vcf"
)
print(f"VCF: {vcf_path}")

# Get all results for an application
results = utils.get_results(
    experiment=experiment,
    application_name="variant_caller"
)
```

## Performance Tips

### Limit fields returned

```python
# Only fetch needed fields
experiments = ii.get_experiments(
    projects=102,
    fields=["pk", "system_id", "sample"]
)
```

### Use count_limit for large queries

```python
# Stop after N results
experiments = ii.get_experiments(
    projects=102,
    count_limit=100
)
```

### Use cursor pagination for very large datasets

```python
experiments = ii.get_instances(
    "experiments",
    projects=102,
    paginator="cursor"
)
```

## Data Model Reference

```
Individual
├── identifier (unique)
├── species (HUMAN, MOUSE, etc.)
├── gender
└── sample_set → [Sample]

Sample
├── identifier
├── individual → Individual
├── category (TUMOR, NORMAL, etc.)
└── experiment_set → [Experiment]

Experiment
├── system_id (unique)
├── sample → Sample
├── technique → Technique
├── platform → Platform
├── raw_data (dict)
├── bam_files (dict)
└── analysis_set → [Analysis]

Analysis
├── pk
├── application → Application
├── targets → [Experiment]
├── references → [Experiment]
├── status (CREATED, STAGED, SUBMITTED, STARTED, SUCCEEDED, FAILED)
├── storage_url (path to results)
└── results (dict)

Application
├── name
├── version
├── assembly
├── species
└── settings (dict)
```

## Jupyter Notebook Pattern

```python
import isabl_cli as ii
import pandas as pd

# Query to DataFrame
experiments = ii.get_experiments(projects=102)
df = pd.DataFrame([
    {
        "system_id": e.system_id,
        "sample": e.sample.identifier,
        "category": e.sample.category,
        "technique": e.technique.method,
    }
    for e in experiments
])
df.head()
```
