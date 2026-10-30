# Docker Compose Installation Commands

## 1. Install Docker Compose on Ubuntu

### Step 1: Update packages

```bash
sudo apt update -y
```

### Step 2: Install Docker and Docker Compose

```bash
sudo apt install docker.io docker-compose-v2 -y
```

If `docker-compose-v2` is unavailable, use Docker's official repository installation method.

### Step 3: Start Docker

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Step 4: Verify installation

```bash
docker --version
docker compose version
```

---

## 2. Install Docker Compose on Amazon Linux 2023

### Step 1: Update packages

```bash
sudo dnf update -y
```

### Step 2: Install Docker

```bash
sudo dnf install docker -y
```

### Step 3: Start Docker

```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### Step 4: Install Docker Compose Plugin

```bash
sudo dnf install docker-compose-plugin -y
```

If the package is unavailable, install the Compose CLI plugin using Docker's official installation instructions.

### Step 5: Verify installation

```bash
docker --version
docker compose version
```

---

## 3. Run Docker Without Sudo (Optional)

For both Ubuntu and Amazon Linux:

```bash
sudo usermod -aG docker $USER
```

Log out and log back in to apply the group change.

Verify:

```bash
docker ps
docker compose version
```

---

## 4. Basic Docker Compose Commands

```bash
# Build images
docker compose build

# Start containers
docker compose up -d

# Build and start containers
docker compose up -d --build

# Check containers
docker compose ps

# View logs
docker compose logs -f

# Stop containers
docker compose stop

# Restart containers
docker compose restart

# Remove containers
docker compose down
```

**Note:** Docker Compose V2 uses `docker compose` (with a space).