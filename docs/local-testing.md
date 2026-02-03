# Local Testing Setup

This guide explains how to run a local Isabl instance for testing skills and the MCP server.

## Prerequisites

- Docker with Docker Compose
- Python 3.9+
- Access to `papaemmelab/isabl_api` (private repo) or pre-built `isabl_demo` images

## Quick Start with isabl_demo Images

If you have the `isabl_demo` images pre-built, this is the fastest method:

### 1. Start the Local API

```bash
cd ~/isabl/isabl_api

# Start containers (use existing images)
docker compose up -d

# Wait for API to start (~30 seconds)
sleep 30

# Verify containers are running
docker ps
```

### 2. Register a Test User

```bash
# Register user
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password1":"testpass123","password2":"testpass123","first_name":"Test","last_name":"User"}' \
  "http://localhost:8000/api/v1/rest-auth/registration/"

# Check Django logs for verification email
docker logs isabl_demo-django-1 2>&1 | grep -A5 "verify-email"

# Extract the verification key and verify email
# Example key format: Ng:1vn3gs:flKDT-y3mGrLVZ6yvJ7Yhm2N2uc
curl -s -X POST -H "Content-Type: application/json" \
  -d '{"key":"YOUR_KEY_HERE"}' \
  "http://localhost:8000/api/v1/rest-auth/registration/verify-email/"

# Login and get token
curl -s -X POST -H 'Content-Type: application/json' \
  --data-raw '{"username":"testuser","password":"testpass123"}' \
  'http://localhost:8000/api/v1/rest-auth/login/'
# Returns: {"key":"your-auth-token"}
```

### 3. Configure isabl-cli

```bash
# Create settings file
mkdir -p ~/.isabl
cat > ~/.isabl/settings.json << 'EOF'
{
    "http://localhost:8000/api/v1/": {
        "api_token": "YOUR_AUTH_TOKEN_HERE"
    }
}
EOF
chmod 600 ~/.isabl/settings.json

# Set environment variable
export ISABL_API_URL="http://localhost:8000/api/v1/"
```

### 4. Install isabl-cli (Development Mode)

```bash
cd ~/isabl/isabl_cli
pip install -e .
```

### 5. Verify Setup

```bash
python3 -c "
import isabl_cli as ii

experiments = list(ii.get_experiments())
print(f'Found {len(experiments)} experiments')

projects = list(ii.get_instances('projects'))
print(f'Found {len(projects)} projects')
"
```

## Services

| Service | Port | Purpose |
|---------|------|---------|
| Django API | 8000 | Main REST API |
| PostgreSQL | 5432 | Database |
| Redis | 6379 | Celery broker |
| Celery Worker | - | Background tasks |
| Celery Beat | - | Scheduled tasks |
| Flower | 5555 | Celery monitoring |

## API Testing

The API requires proper headers:

```bash
TOKEN="your-auth-token"

# List projects (use Accept header, no trailing slash)
curl -s -H "Accept: application/json" \
  -H "Authorization: Token $TOKEN" \
  'http://localhost:8000/api/v1/projects'

# List experiments
curl -s -H "Accept: application/json" \
  -H "Authorization: Token $TOKEN" \
  'http://localhost:8000/api/v1/experiments'
```

## Testing the MCP Server

Once the local API is running:

```bash
cd ~/isabl/isabl-ai-integration/mcp-server

# Create .env file
cat > .env << EOF
ISABL_MCP_ISABL_API_URL=http://localhost:8000/api/v1/
ISABL_MCP_ISABL_API_TOKEN=your-test-token
ISABL_MCP_LLM_PROVIDER=openai
ISABL_MCP_OPENAI_API_KEY=your-openai-key
EOF

# Run MCP server
python -m isabl_mcp.server
```

## Testing Skills

Skills can be tested by:

1. Installing them to `~/.claude/skills/`
2. Opening Claude Code in a test project
3. Invoking the skill with `/skill-name`

```bash
# Install skills
./scripts/install-skills.sh

# Test in Claude Code
cd ~/isabl/isabl_cli
claude
# Then type: /isabl-write-app
```

## Stopping Services

```bash
cd ~/isabl/isabl_api
docker compose down

# To also remove volumes (reset database):
docker compose down -v
```

## Apple Silicon Notes

If building from source on Apple Silicon (M1/M2/M3):
- Base images may be x86 (amd64), requiring emulation
- Consider increasing Docker Desktop memory allocation in preferences
- Use pre-built `isabl_demo` images when available for faster startup

## Troubleshooting

### API won't start
```bash
# Check logs
docker logs isabl_demo-django-1

# Check all container statuses
docker ps -a
```

### Docker not running
```bash
# On macOS, ensure Docker Desktop is running
open -a Docker

# On Linux, start the Docker daemon
sudo systemctl start docker
```

### Database connection issues
```bash
# Check postgres is running
docker ps | grep postgres

# View postgres logs
docker logs isabl_demo-postgres-1
```

### Permission denied on settings.json
```bash
chmod 600 ~/.isabl/settings.json
```
