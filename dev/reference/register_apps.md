# register_apps Analysis

> CLI for Registering Versioned Containerized Applications

**Repository**: `papaemmelab/register_apps`
**Language**: Python
**CLI Framework**: Click
**Version**: 2.0.1

## Purpose

Register Apps manages installation of applications with:
- Version isolation via virtual environments
- Container runtimes (Singularity/Docker)
- Executable wrapper scripts
- Multiple versions coexisting

**Use case**: Production deployment of bioinformatics pipelines with consistent versioning.

## Key Commands

| Command | Purpose |
|---------|---------|
| `register_toil` | Register Toil container pipelines |
| `register_singularity` | Register Singularity container commands |
| `register_docker` | Register Docker container commands |
| `register_python` | Register pure Python packages |

## Configuration

### Environment Variables

```bash
REGISTER_APPS_BIN=/work/isabl/bin      # Executable symlink directory
REGISTER_APPS_OPT=/work/isabl/local    # Versioned install directory
REGISTER_APPS_VOLUMES=/data1:/data1    # Container volume mounts
```

### Command Options

```bash
register_toil \
  --pypi_name mypackage \
  --pypi_version 1.0.0 \
  --python python3 \
  --container singularity \
  --image_user papaemmelab \
  --environment production \
  --bindir /work/isabl/bin \
  --optdir /work/isabl/local \
  --volumes /data:/data
```

## Directory Structure Created

```
/work/isabl/bin/
└── app_name_version → (symlink to optdir)

/work/isabl/local/{app_name}/{version}/
├── {app_name}                    # Executable wrapper
├── {app_name}-{version}.simg     # Singularity image
└── docker-{app_name}-{version}   # Docker reference
```

## Execution Model

1. **Toil**: Bash wrapper sources venv, calls toil with container options
2. **Singularity**: `singularity exec` with mounted volumes
3. **Docker**: `docker run` with mounted volumes
4. **Python**: Direct venv executable call

## Virtual Environment Management

- Uses `virtualenvwrapper`
- Environment naming: `{environment}__{app_name}__{version}`
- Supports Python 2 and Python 3
- Isolated per application version

## Integration with Isabl

- Default paths reference `/work/isabl/`
- Standalone tool that works within isabl ecosystem
- No direct code dependency on isabl_cli

## Key Concepts for AI Agents

1. **Deployment tool**: Not a library, CLI-only interface
2. **Version isolation**: Each version in separate directory
3. **Container integration**: Optional but central to architecture
4. **Virtual environments**: Mandatory for installations
5. **Idempotent**: `--force` controls overwrite behavior
