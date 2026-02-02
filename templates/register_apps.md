# Register Apps

> CLI for registering versioned containerized applications

## Purpose

Deploy bioinformatics tools with version isolation:
- Virtual environment per version
- Container runtime support (Singularity/Docker)
- Executable wrapper scripts
- Multiple versions coexist

## Commands

### Register Toil Pipeline
```bash
register_toil \
  --pypi_name toil_variant_caller \
  --pypi_version 2.0.0 \
  --container singularity \
  --image_user papaemmelab \
  --python python3 \
  --environment production
```

### Register Singularity Container
```bash
register_singularity \
  --target bwa_mem \
  --command bwa \
  --image_repository bwa \
  --image_version 0.7.17
```

### Register Docker Container
```bash
register_docker \
  --target samtools \
  --command samtools \
  --image_repository samtools \
  --image_version 1.15
```

### Register Python Package
```bash
register_python \
  --pypi_name my_tool \
  --pypi_version 1.0.0 \
  --python python3
```

## Configuration

### Environment Variables
```bash
REGISTER_APPS_BIN=/work/isabl/bin      # Executable symlinks
REGISTER_APPS_OPT=/work/isabl/local    # Versioned installs
REGISTER_APPS_VOLUMES=/data1:/data1    # Container mounts
```

### Common Options

| Option | Purpose |
|--------|---------|
| `--bindir` | Where executables are symlinked |
| `--optdir` | Where versions are installed |
| `--volumes` | Volume mounts for containers |
| `--force` | Overwrite existing installation |
| `--environment` | production/development/testing |

## Directory Structure

```
/work/isabl/bin/
└── app_name_version → symlink

/work/isabl/local/{app_name}/{version}/
├── {app_name}                    # Executable wrapper
├── {app_name}-{version}.simg     # Singularity image
└── docker-{app_name}-{version}   # Docker reference
```

## Requirements

- virtualenvwrapper installed
- singularity or docker available
- Write access to bindir and optdir
