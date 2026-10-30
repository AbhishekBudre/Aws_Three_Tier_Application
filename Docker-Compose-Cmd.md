# Docker Compose Commands Cheat Sheet

## 1. Install Docker Compose on Ubuntu

### Step 1: Update Ubuntu packages

```bash
sudo apt update
sudo apt upgrade -y
```

### Step 2: Install Docker prerequisites

```bash
sudo apt install ca-certificates curl -y
```

### Step 3: Add Docker's official GPG key

```bash
sudo install -m 0755 -d /etc/apt/keyrings

sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg \
-o /etc/apt/keyrings/docker.asc

sudo chmod a+r /etc/apt/keyrings/docker.asc
```

### Step 4: Add Docker repository

```bash
echo \
"deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
$(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}") stable" | \
sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```

### Step 5: Update package index

```bash
sudo apt update
```

### Step 6: Install Docker Engine and Docker Compose plugin

```bash
sudo apt install docker-ce docker-ce-cli containerd.io \
docker-buildx-plugin docker-compose-plugin -y
```

### Step 7: Verify Docker installation

```bash
docker --version
docker compose version
```

### Step 8: Start Docker service

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Step 9: Verify Docker service

```bash
sudo systemctl status docker
```

### Step 10: Run Docker without sudo (Optional)

```bash
sudo usermod -aG docker $USER
```

Log out and log back in for the group change to take effect.

Verify:

```bash
docker ps
docker compose version
```

---

## 2. Docker Compose Commands

### Validate Compose Configuration

```bash
docker compose config
```

### Build Docker Images

```bash
docker compose build
```

Build without cache:

```bash
docker compose build --no-cache
```

### Start Containers

```bash
docker compose up -d
```

Build and start:

```bash
docker compose up -d --build
```

### Check Running Containers

```bash
docker compose ps
```

### View Logs

```bash
docker compose logs -f
```

Individual service logs:

```bash
docker compose logs database
docker compose logs backend
docker compose logs frontend
```

### Stop Containers

```bash
docker compose stop
```

### Start Existing Containers

```bash
docker compose start
```

### Restart Containers

```bash
docker compose restart
```

### Remove Containers

```bash
docker compose down
```

### Access Containers

```bash
docker compose exec database bash
docker compose exec backend bash
docker compose exec frontend sh
```

### Connect to PostgreSQL

```bash
docker compose exec database psql -U admin -d mydatabase
```

### Check Database Readiness

```bash
docker compose exec database pg_isready -U admin -d mydatabase
```

### View Inventory Records

```bash
docker compose exec database psql -U admin -d mydatabase -c "SELECT * FROM inventory;"
```

### Check Docker Resources

```bash
docker images
docker volume ls
docker network ls
docker ps -a
```

### Remove Everything Including Volumes

```bash
docker compose down -v --rmi local
```

**Warning:** This removes the Compose-managed database volume and permanently deletes its stored data.

---

## 3. Daily Deployment Workflow

Run these commands from your project root directory:

```bash
# Validate configuration
docker compose config

# Build images
docker compose build

# Start all services
docker compose up -d

# Check containers
docker compose ps

# View logs
docker compose logs -f

# Stop and remove containers
docker compose down
```

---

**Project:** Inventory Management Dashboard

**Technologies:** Docker, Docker Compose, PostgreSQL, Python Flask, Gunicorn, Nginx, Prometheus.

**Purpose:** Learn Docker installation, Compose configuration, multi-container deployment, networking, and database persistence.