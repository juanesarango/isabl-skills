# Example Notebooks

> Jupyter notebooks demonstrating common Isabl workflows

**Source**: Local `~/isabl/notebooks/`

## Overview

31 Jupyter notebooks showing real-world usage patterns for:
- Data exploration and fetching
- Result merging and aggregation
- HPC job monitoring
- Project analysis
- Visualization

## Categories

| Category | Count | Purpose |
|----------|-------|---------|
| Data Fetching | 7 | Query and retrieve data from Isabl |
| Visualization | 8 | HPC benchmarks, plots, metrics |
| Result Merging | 3 | Combine outputs across analyses |
| Job Management | 6 | Status tracking, restart commands |
| Project Analysis | 3 | Storage footprint, project metrics |
| Specialized | 4 | IGV links, gene analysis |

## Common Patterns

### Pattern 1: Query and Fetch

```python
import isabl_cli as ii

# Query analyses with filters
analyses = ii.get_analyses(
    projects__pk__in=[444],
    application__name__in=["BATTENBERG", "MUTECT"],
    status="SUCCEEDED",
    fields="pk,status,application__name,targets__system_id,results"
)

# Get experiments by system_id
experiments = ii.get_instances(
    "experiments",
    system_id__in=sample_ids,
    fields="pk,system_id"
)
```

### Pattern 2: Access Results

```python
# Read result files directly
for a in analyses:
    df = pd.read_csv(a.results["pass_tsv"], sep='\t', compression='gzip')
    vcf_path = a.results["vcf"]
    storage_path = a.storage_url
```

### Pattern 3: Merge Results

```python
# Combine TSVs from multiple analyses
dfs = []
for a in tqdm(analyses):
    df = pd.read_csv(a.results["pass_coding_tsv"], sep='\t', compression='gzip')
    df['analysis_pk'] = a.pk
    dfs.append(df)

merged_df = pd.concat(dfs, ignore_index=True)
```

### Pattern 4: Status Monitoring

```python
# Track analysis status
for a in analyses:
    if a.status != "SUCCEEDED":
        print(f"{a.application.name}[{a.pk}]: {a.status}")
        print(f"https://isabl.mskcc.org/?analysis={a.pk}")
```

### Pattern 5: Build CLI Commands

```python
# Generate commands for batch operations
for a in analyses:
    target = a.targets[0].system_id
    reference = a.references[0].system_id

    cmd = f"isabl apps-grch37 battenberg-1.4.0_forcecn \\
        -p {target} {reference} \\
        --rho={purity} --psi={ploidy} \\
        --commit"

    print(cmd)
```

### Pattern 6: File System Navigation

```python
from pathlib import Path
from glob import glob

# Navigate analysis storage
for a in analyses:
    # Read job IDs
    jobs_txt = Path(a.storage_url) / "job_ids.txt"

    # Find subdirectories
    for outdir in glob(f"{a.storage_url}/subclones_*"):
        # Process results
        pass
```

## Key Notebooks

| Notebook | Purpose |
|----------|---------|
| `ExampleIsabl.ipynb` | Basic isabl_cli introduction |
| `AnalysesTracker.v1.ipynb` | Track analysis status across projects |
| `HPC Benchmark.ipynb` | Visualize job resource usage |
| `DroppingCavemanBenchmark.ipynb` | Merge variant caller results |
| `Isabl Projects Footprint.ipynb` | Analyze storage usage |
| `IGV Example.ipynb` | Generate IGV browser links |

## Library Dependencies

```python
# Core
import isabl_cli as ii
import pandas as pd

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
from upsetplot import UpSet

# Progress
from tqdm.notebook import tqdm

# Utilities
from pathlib import Path
from glob import glob
import gzip
```

## Statistics from Notebooks

From HPC Benchmark notebooks:
- 75,342 total jobs analyzed
- 27 applications tracked
- 60+ TB total memory used
- 1.36 TB storage footprint
- Top apps by jobs: CAVEMAN (17K), MUTECT (7K), BATTENBERG (1.5K)
