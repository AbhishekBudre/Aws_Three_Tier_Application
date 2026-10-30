# Inventory Management Dashboard

A three-tier Inventory Management application built using **PostgreSQL, Python Flask, Gunicorn, Prometheus metrics, Nginx, and Docker**.

## 1. Project Overview

This project allows users to manage inventory products through a web dashboard.

### Technologies Used

- **Frontend:** HTML, CSS, JavaScript, Nginx
- **Backend:** Python, Flask, Gunicorn
- **Database:** PostgreSQL
- **Monitoring:** Prometheus metrics
- **Containerization:** Docker

### Features

- Add new inventory products
- View all products
- Update product details
- Delete products
- Track quantities and prices
- Calculate total stock value
- Monitor backend health and readiness
- Expose Prometheus metrics
- Persist PostgreSQL data using a Docker named volume

## 2. Project Folder Structure

```text
Inventory-Management/
├── database/
│   ├── create_table.sql
│   ├── .env
│   └── Dockerfile
├── backend/
│   ├── .env
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
└── frontend/
    ├── index.html
    ├── style.css
    ├── app.js
    ├── nginx.conf
    └── Dockerfile
```

## 3. Prerequisites

Install the following tools on your Ubuntu server:

- Docker Engine
- Git (if cloning from a repository)
- An SSH client for connecting to EC2

Verify your Docker installation:

```bash
docker --version
docker info
```

## 4. Database Configuration

### File: `database/.env`

```env
POSTGRES_USER=admin
POSTGRES_PASSWORD=12345
POSTGRES_DB=mydatabase
```

These environment variables configure the PostgreSQL database.

**Security:** The example password is for learning only. Use a strong password and a suitable secrets-management solution for production deployments.

### File: `database/create_table.sql`

This file creates the inventory table and inserts sample products.

PostgreSQL executes scripts in `/docker-entrypoint-initdb.d/` when initializing a fresh data directory.

### File: `database/Dockerfile`

```dockerfile
FROM postgres:13

ENV POSTGRES_USER=admin
ENV POSTGRES_DB=mydatabase

COPY create_table.sql /docker-entrypoint-initdb.d/

EXPOSE 5432
```

## 5. Backend Configuration

### File: `backend/.env`

```env
DB_HOST=my_postgres
DB_PORT=5432
DB_NAME=mydatabase
DB_USERNAME=admin
DB_PASSWORD=12345
DB_SSLMODE=prefer

FLASK_HOST=0.0.0.0
FLASK_PORT=5000
```

The `DB_HOST` value must resolve to the PostgreSQL container through the shared Docker network.

### File: `backend/requirements.txt`

```text
Flask==3.1.0
Flask-Cors==5.0.0
Werkzeug==3.1.3
psycopg2-binary==2.9.10
prometheus-flask-exporter==0.23.2
gunicorn==23.0.0
python-dotenv==1.0.1
```

The backend source code is stored in `backend/app.py`. It provides the inventory CRUD API and monitoring endpoints.

### File: `backend/Dockerfile`

```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--access-logfile", "-", "app:app"]
```

## 6. Frontend Configuration

The frontend contains:

- `index.html` — Dashboard structure
- `style.css` — Dashboard styling
- `app.js` — API requests and inventory operations
- `nginx.conf` — Web server and API reverse proxy
- `Dockerfile` — Frontend container image

The Nginx configuration forwards API requests to the backend container named `inventory_backend` on port `5000`.

### File: `frontend/Dockerfile`

```dockerfile
FROM nginx:alpine

COPY index.html /usr/share/nginx/html/index.html
COPY style.css /usr/share/nginx/html/style.css
COPY app.js /usr/share/nginx/html/app.js
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

## 7. Deployment Instructions

Run the following commands from the `Inventory-Management` project root directory.

### Step 1: Create a Docker Network

Create a shared network so the frontend, backend, and database can communicate.

```bash
docker network create inventory-network
```

### Step 2: Build the Database Image

```bash
docker build -t inventory-database:dev ./database
```

### Step 3: Create a Docker Volume for Data Persistence

Create a named Docker volume to store PostgreSQL database files independently of the database container's lifecycle.

```bash
docker volume create inventory_data
```

Verify that the volume exists:

```bash
docker volume ls
```

Inspect the volume details:

```bash
docker volume inspect inventory_data
```

**Important:** Do not remove this volume if you want to retain your database data.

### Step 4: Run the PostgreSQL Container

Start PostgreSQL and mount the named volume at its data directory.

```bash
docker run -d \
  --name my_postgres \
  --network inventory-network \
  --network-alias my_postgres \
  --env-file ./database/.env \
  -p 5432:5432 \
  -v inventory_data:/var/lib/postgresql/data \
  inventory-database:dev
```

The `-v inventory_data:/var/lib/postgresql/data` option mounts the named volume inside the PostgreSQL container.

This allows database files to persist when the container is stopped or removed, provided the volume is retained.

### Step 5: Wait for PostgreSQL

On Ubuntu, run:

```bash
until docker exec my_postgres pg_isready -U admin -d mydatabase; do
  sleep 2
done
```

Continue when PostgreSQL reports that it is accepting connections.

### Step 6: Build the Backend Image

```bash
docker build -t inventory-backend:dev ./backend
```

### Step 7: Run the Backend Container

```bash
docker run -d \
  --name inventory_backend \
  --network inventory-network \
  --env-file ./backend/.env \
  -p 5000:5000 \
  inventory-backend:dev
```

### Step 8: Build the Frontend Image

```bash
docker build -t inventory-frontend:dev ./frontend
```

### Step 9: Run the Frontend Container

```bash
docker run -d \
  --name inventory_frontend \
  --network inventory-network \
  -p 3000:80 \
  inventory-frontend:dev
```

## 8. Verify the Deployment

### Check Running Containers

```bash
docker ps
```

All three containers should be running:

- `my_postgres`
- `inventory_backend`
- `inventory_frontend`

### Check Container Logs

```bash
docker logs my_postgres
docker logs inventory_backend
docker logs inventory_frontend
```

### Check Backend Health

```bash
curl http://localhost:5000/health
```

Expected response, assuming the endpoint returns this structure:

```json
{
  "status": "healthy",
  "service": "inventory-backend"
}
```

### Check Database Readiness

```bash
curl http://localhost:5000/ready
```

### Retrieve Inventory Products

```bash
curl http://localhost:5000/api/items
```

### Check Prometheus Metrics

```bash
curl http://localhost:5000/metrics
```

### Test the Frontend

Open the following URL in your browser:

```text
http://YOUR-EC2-PUBLIC-IP:3000
```

Replace `YOUR-EC2-PUBLIC-IP` with your EC2 instance's public IPv4 address.

## 9. Verify Database Data Persistence

This test checks that your inventory data remains available after removing and recreating the PostgreSQL container.

### Step 1: View Existing Inventory Records

```bash
docker exec -it my_postgres \
  psql -U admin -d mydatabase \
  -c "SELECT * FROM inventory;"
```

### Step 2: Stop and Remove the Database Container

```bash
docker stop my_postgres
docker rm my_postgres
```

These commands remove the container, **not** the named volume.

### Step 3: Recreate the PostgreSQL Container

Run the same command used in Step 4:

```bash
docker run -d \
  --name my_postgres \
  --network inventory-network \
  --network-alias my_postgres \
  --env-file ./database/.env \
  -p 5432:5432 \
  -v inventory_data:/var/lib/postgresql/data \
  inventory-database:dev
```

Wait until PostgreSQL is ready:

```bash
until docker exec my_postgres pg_isready -U admin -d mydatabase; do
  sleep 2
done
```

### Step 4: Verify the Records Again

```bash
docker exec -it my_postgres \
  psql -U admin -d mydatabase \
  -c "SELECT * FROM inventory;"
```

Your previously stored records should still be available because the same volume, `inventory_data`, is attached to the recreated container.

**Note:** PostgreSQL initialization scripts run only when the data directory is initialized for the first time. Reusing an existing volume does not automatically rerun `create_table.sql`.

## 10. Useful Docker Commands

### List All Containers

```bash
docker ps -a
```

### List Images

```bash
docker images
```

### Stop Containers

```bash
docker stop inventory_frontend inventory_backend my_postgres
```

### Start Existing Containers

```bash
docker start my_postgres inventory_backend inventory_frontend
```

### Remove Containers

Stop the containers first, then run:

```bash
docker rm inventory_frontend inventory_backend my_postgres
```

### Remove Project Images

```bash
docker rmi inventory-frontend:dev inventory-backend:dev inventory-database:dev
```

### View Network Details

```bash
docker network inspect inventory-network
```

### View Database Volume

```bash
docker volume inspect inventory_data
```

### Remove the Volume — Destructive

Only run this command if you intentionally want to delete the persistent database storage and its contents:

```bash
docker volume rm inventory_data
```

**Warning:** Removing a container does not automatically remove its named volume. Deleting the volume can permanently remove the stored database data.

## 11. Troubleshooting

### Database Connection Error

Check the database logs:

```bash
docker logs my_postgres
```

Verify PostgreSQL is accepting connections:

```bash
docker exec my_postgres pg_isready -U admin -d mydatabase
```

Ensure the backend and database share the `inventory-network` network and that their credentials match.

### Frontend Cannot Reach Backend

Check the Nginx logs:

```bash
docker logs inventory_frontend
```

Check the backend logs:

```bash
docker logs inventory_backend
```

Verify that `frontend/nginx.conf` uses the correct backend container name and port.

### Port Already in Use

Check whether ports `3000`, `5000`, or `5432` are already occupied:

```bash
sudo ss -lntp
```

If necessary, change the host-side port mapping.

### Database Table Is Missing

Check whether the table exists:

```bash
docker exec -it my_postgres \
  psql -U admin -d mydatabase \
  -c "\dt"
```

Initialization scripts execute only when PostgreSQL initializes an empty data directory. If the volume already contains a database, you may need to apply schema changes manually.

### Container Name Already Exists

If Docker reports that a container with the requested name already exists, inspect your containers:

```bash
docker ps -a
```

Start the existing container if appropriate, or remove it before recreating it. Do not remove the database volume unless you intend to delete the stored data.

## 12. AWS EC2 Security Group

For a learning environment, configure inbound rules as needed:

| Port | Purpose | Recommended access |
|---|---|---|
| 22 | SSH | Your IP address only |
| 3000 | Web dashboard | Your IP address or approved users |
| 5000 | Backend API | Keep private if only Nginx needs access |
| 5432 | PostgreSQL | Keep private; do not expose publicly |

The Docker commands above publish ports `5000` and `5432` on the EC2 host. For production, avoid exposing the backend and database publicly. Restrict access using security groups, host firewall rules, and private container networking.

## 13. Application Architecture

```text
User Browser
     |
     | HTTP :3000
     v
Nginx Frontend
     |
     | /api/ requests
     v
Flask Backend :5000
     |
     | PostgreSQL :5432
     v
PostgreSQL Database
```

Prometheus metrics are exposed by the Flask backend at `/metrics`.

PostgreSQL stores its data in the persistent Docker volume named `inventory_data`.

## 14. Important Notes

- Keep the database password out of public Git repositories.
- Use HTTPS for public deployments.
- Back up PostgreSQL data regularly.
- The dashboard uses a PostgreSQL named volume for data persistence.
- Keep database and backend ports private unless external access is specifically required.
- The example is intended for learning and should be hardened before production use.

---

**Project:** Inventory Management Dashboard  
**Technologies:** Docker, PostgreSQL, Python Flask, Gunicorn, Nginx, Prometheus  
**Purpose:** Learn multi-container deployment, CRUD operations, monitoring, and three-tier application architecture.