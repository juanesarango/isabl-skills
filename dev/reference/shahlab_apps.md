# shahlab_apps

> Research bioinformatics applications from Shah Lab

**Source**: `shahcompbio/shahlab_apps`

## Overview

Contains 111 AbstractApplication subclasses covering advanced research workflows:
- Whole genome sequencing (WGS)
- Single-cell DNA (scDNA)
- Single-cell RNA (scRNA)
- Oxford Nanopore (ONT)
- Spatial transcriptomics
- HMFTools integration

## App Categories

| Category | Count | Examples |
|----------|-------|----------|
| WGS | 27 | WGS-ALIGNMENT, WGS-SOMATICCALLING, WGS-REMIXT |
| scDNA | 16 | SCDNA-ALIGNMENT, SCDNA-HMMCOPY, SCDNA-MEDICC2 |
| scRNA | 43 | CELLRANGER, CELLASSIGN, SCVELO, VDJ_ANALYSIS |
| ONT | 24 | ONT-NANOSEQ, ONT-DEEPSOMATIC, ONT-WHATSHAP |
| Mondrian | 9 | MONDRIAN-QC, MONDRIAN-VARIANTCALLING |
| HMFTools | 8 | HMFTools-Sage, HMFTools-Purple, HMFTools-Linx |
| CFDNA | 2 | CFDNA-NUCLEO, CFDNA-QC |
| Spatial | 1 | SPACERANGER |

## Pipeline Types

| Type | Description | Examples |
|------|-------------|----------|
| CWL-based | Common Workflow Language | CFDNA pipelines |
| Nextflow | nf-core compatible | ONT, Mondrian, RNAFUSION |
| Singularity | Container-based | WGS, scRNA |
| Shell/Python | Direct script execution | DLP, some tools |

## scRNA Subcategories

| Subcategory | Apps | Purpose |
|-------------|------|---------|
| GEX | CELLRANGER, CELLASSIGN, SCVELO | Gene expression |
| CITE-Seq | CELLRANGER_CITESEQ | Protein + RNA |
| VDJ | CELLRANGER_VDJ, TCRDIST, GLIPH2 | Immune repertoire |
| ATAC | CELLRANGER_ATAC | Chromatin accessibility |
| Multiome | CELLRANGER-ARC | GEX + ATAC |

## ONT (Long-read) Apps

| App | Purpose |
|-----|---------|
| ONT-NANOSEQ | Long-read sequencing pipeline |
| ONT-DEEPSOMATIC | DeepSomatic variant calling |
| ONT-WHATSHAP | Haplotype phasing |
| ONT-nanomonsv | SV calling |
| ONT-severus | SV algorithm |
| ONT-bambu-merge | Transcript assembly |

## Single-Cell DNA Workflow

```
SCDNA-ALIGNMENT
    ↓
SCDNA-HMMCOPY (copy number)
    ↓
SCDNA-SIGNALS (signal detection)
    ↓
SCDNA-MEDICC2 (phylogenetic inference)
    ↓
SCDNA-SITKA (clonal evolution)
```

## HMFTools Integration

Hartwig Medical Foundation tools for comprehensive WGS analysis:

| Tool | Purpose |
|------|---------|
| Amber | BAF analysis |
| Cobalt | GC correction |
| Sage | Somatic calling |
| Pave | VCF annotation |
| Gridss | SV detection |
| Gripss | SV filtering |
| Purple | Purity/ploidy |
| Linx | SV interpretation |

## Key Patterns

### Nextflow Integration

```python
class RNAFusionGRCh38(AbstractApplication):
    NAME = "RNAFUSION"

    def get_command(self, analysis, inputs, settings):
        return f"""
        nextflow run nf-core/rnafusion \\
            --input {inputs['samplesheet']} \\
            --outdir {analysis.storage_url} \\
            -profile singularity
        """
```

### Multi-Modal Apps

Many apps support multiple modes:
- `MEDICC2` has AS mode, TCN mode, SITKA integration
- `ONT-WHATSHAP` has haplotag variant
- `SIGNALS` has filtered/unfiltered modes

## Key Files

```
shahlab_apps/
├── shahlab_apps/
│   └── apps/
│       ├── wgs/           # WGS pipelines
│       ├── scdna/         # Single-cell DNA
│       ├── scrna/         # Single-cell RNA
│       ├── ont/           # Oxford Nanopore
│       ├── mondrian/      # Nextflow SC pipelines
│       ├── hmftools/      # Hartwig tools
│       └── ...
└── settings.py
```
