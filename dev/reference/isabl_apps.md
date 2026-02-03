# isabl_apps

> Production bioinformatics applications for Isabl

**Source**: `papaemmelab/isabl_apps`

## Overview

Contains 63 AbstractApplication subclasses covering the core bioinformatics workflows:
- Alignment (BWA, STAR, CellRanger)
- Variant calling (Mutect, Strelka, Caveman, Pindel)
- Copy number (Battenberg, FACETS, CNVKit, ACE)
- Structural variants (BRASS, GRIDSS, SVABA, Manta)
- Fusions (STAR-Fusion, FusionCatcher, FuSeq, Cicero)
- Quality control (Conpair, Somalier, Mosdepth, MSISensor)
- Annotation (VEP, TOPIARY, FFPErase)

## App Categories

| Category | Count | Examples |
|----------|-------|----------|
| Alignment | 4 | BWA_MEM, STAR, CELLRANGER, SALMON |
| Variant Calling (SNV/Indel) | 8 | MUTECT, STRELKA, CAVEMAN, PINDEL, FREEBAYES |
| Structural Variants | 5 | BRASS, GRIDSS, SVABA, MANTA, JABBA |
| Copy Number | 7 | BATTENBERG, FACETS, CNVKIT, ACE, PURPLE, CNACS |
| Fusions | 5 | STARFUSION, FUSIONCATCHER, FUSEQ, CICERO, ANNOTFUSIONS |
| QC | 6 | CONPAIR, SOMALIER, MOSDEPTH, MSISENSOR, QC_DATA |
| Annotation | 5 | ANNOT_*, TOPIARY, FFPERASE, VAGRENT |
| Telomere | 3 | TELOMERECAT, TELOMEREHUNTER, TELSEQ |
| Other | 20 | HLA_TYPE, CLONALITY, VIPER, etc. |

## Input Patterns

| Pattern | Count | Description |
|---------|-------|-------------|
| TARGETS | 33 | Single sample input |
| PAIRS | 22 | Tumor-normal pairs |
| INDIVIDUALS | 8 | Individual-level or custom grouping |

## Common Patterns

### Basic App Structure

```python
from isabl_cli import AbstractApplication, options

class MutectGRCh37(AbstractApplication):
    NAME = "MUTECT"
    VERSION = "1.0.0"
    ASSEMBLY = "GRCh37"
    SPECIES = "HUMAN"

    cli_options = [options.PAIRS]

    application_settings = {
        "tool_path": "/path/to/mutect",
        "threads": 4,
    }

    def validate_experiments(self, targets, references):
        assert len(targets) == 1
        assert len(references) == 1
        assert targets[0].technique.method == "WGS"

    def get_command(self, analysis, inputs, settings):
        return f"""
        {settings.tool_path} \\
            --tumor {analysis.targets[0].bam_files["GRCh37"]["url"]} \\
            --normal {analysis.references[0].bam_files["GRCh37"]["url"]} \\
            --output {analysis.storage_url}/output.vcf
        """

    def get_analysis_results(self, analysis):
        return {"vcf": f"{analysis.storage_url}/output.vcf"}
```

### Apps with Dependencies

```python
def get_dependencies(self, targets, references, settings):
    from isabl_cli import utils

    # Get BAM from alignment app
    bam, alignment_analysis = utils.get_result(
        experiment=targets[0],
        application_key=settings.alignment_app_pk,
        result_key="bam"
    )

    return [alignment_analysis], {"input_bam": bam}
```

### Multi-Step Apps (Battenberg pattern)

```
BATTENBERG
├── battenberg-1.0.0          # Initial run
├── battenberg-1.0.0_refitcn  # Refit copy number
├── battenberg-1.0.0_forcecn  # Force specific values
└── battenberg-1.0.0_finalise # Finalize results
```

## Assembly Variants

Many apps have multiple versions for different reference genomes:
- `MutectGRCh37` / `MutectGRCh38`
- `BattenbergGRCh37` / `BattenbergGRCh38`
- Apps may also have mouse variants (`GRCm38`)

## Key Files

```
isabl_apps/
├── isabl_apps/
│   └── apps/
│       ├── mutect/
│       │   └── __init__.py
│       ├── battenberg/
│       │   └── __init__.py
│       └── ...
├── settings.py              # Default settings
└── __init__.py              # INSTALLED_APPLICATIONS
```
