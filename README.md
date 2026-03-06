# News Capstone – Django Application

A Django news platform where **Readers** subscribe to publishers and journalists, **Journalists** submit articles, and **Editors** approve them. On approval, subscribers receive email notifications and a post is made to X (Twitter).

---

## Table of Contents

1. [Features](#features)
2. [Project Structure](#project-structure)
3. [Setup Option A – Virtual Environment (Local Development)](#setup-option-a--virtual-environment-local-development)
4. [Setup Option B – Docker (Containerised)](#setup-option-b--docker-containerised)
5. [Secrets & Credentials](#secrets--credentials)
6. [Sphinx Documentation](#sphinx-documentation)
7. [Running Tests](#running-tests)
8. [REST API](#rest-api)
9. [Git Branch Structure](#git-branch-structure)

---

## Features

- Custom user model with three roles: **Reader**, **Editor**, **Journalist**
- Group/permission assignment per role (set automatically on registration)
- Editorial approval workflow — articles must be approved before readers can see them
- Email notifications sent to subscribed readers on article approval
- X (Twitter) post on article approval
- REST API endpoint returning subscription-filtered articles for readers
- Automated tests for the REST API

---

## Project Structure

```
news_capstone_consolidation/
├── Dockerfile
├── .dockerignore
├── .gitignore
├── .flake8
├── requirements.txt
├── secrets.example.txt       ← copy this to .env and fill in real values
├── README.md
├── docs/                     ← Sphinx documentation source
│   ├── conf.py
│   ├── index.rst
│   ├── Makefile
│   ├── make.bat
│   ├── modules/              ← one .rst file per Python module
│   └── _build/html/          ← generated HTML docs (committed for reviewer access)
├── planning/                 ← design documents
└── news_project/             ← Django project root (contains manage.py)
    ├── manage.py
    ├── news_project/         ← Django settings, urls, wsgi, asgi
    │   └── settings.py
    ├── news_app/             ← main Django app
    │   ├── models.py
    │   ├── views.py
    │   ├── api_views.py
    │   ├── serializers.py
    │   ├── forms.py
    │   ├── notifications.py
    │   ├── signals.py
    │   ├── admin.py
    │   ├── tests.py
    │   ├── urls.py
    │   └── api_urls.py
    └── templates/            ← HTML templates
```

---

## Setup Option A – Virtual Environment (Local Development)

Use this path if you want to run the project directly on your machine using Python and a local MySQL/MariaDB database.

### Prerequisites

- Python 3.10 or later
- MySQL or MariaDB server running locally
- `mysqlclient` system libraries (see below)

### Step 1 – Create and activate a virtual environment

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell):**
```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 2 – Install dependencies

```bash
pip install -r requirements.txt
```

> **Note:** `mysqlclient` requires C libraries.
> - macOS: `brew install mysql-client pkg-config`
> - Ubuntu/Debian: `sudo apt install default-libmysqlclient-dev build-essential pkg-config`
> - Windows: Use the pre-built wheel from https://www.lfd.uci.edu/~gohlke/pythonlibs/

### Step 3 – Configure the database

Create the MySQL database and user:

```sql
CREATE DATABASE news_app_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'news_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON news_app_db.* TO 'news_user'@'localhost';
FLUSH PRIVILEGES;
```

### Step 4 – Set environment variables

Copy the example secrets file and fill in your values:

```bash
cp secrets.example.txt .env
```

Then set the variables in your shell (or use a tool like `python-dotenv`):

```bash
export DJANGO_SECRET_KEY="a-long-random-secret-key"
export DB_PASSWORD="your_password"
# (set other variables as needed — see secrets.example.txt)
```

### Step 5 – Run migrations

```bash
cd news_project
python manage.py migrate
```

### Step 6 – Create a superuser (optional)

```bash
python manage.py createsuperuser
```

### Step 7 – Start the development server

```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000/

---

## Setup Option B – Docker (Containerised)

Use this path if you want to build and run the application inside a Docker container. This does **not** require Python, MySQL, or any other dependencies to be installed on your machine — only Docker.

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running

### Using SQLite (quickest, no MySQL required)

This is the easiest way to test the Docker image without needing an external database.

**Step 1 – Build the image:**
```bash
docker build -t news-capstone .
```

**Step 2 – Run the container:**
```bash
docker run -p 8000:8000 \
  -e DJANGO_SECRET_KEY="replace-with-a-secure-key" \
  -e DJANGO_DEBUG="true" \
  -e DB_ENGINE="django.db.backends.sqlite3" \
  -e DB_NAME="db.sqlite3" \
  news-capstone
```

**Step 3 – Open in your browser:**

http://localhost:8000/

### Using MySQL (matches production setup)

**Step 1 – Ensure a MySQL server is accessible from Docker.**

If MySQL is running on your host machine, use `host.docker.internal` as the host on macOS/Windows. On Linux, use your machine's LAN IP address.

**Step 2 – Build the image:**
```bash
docker build -t news-capstone .
```

**Step 3 – Run with MySQL environment variables:**
```bash
docker run -p 8000:8000 \
  -e DJANGO_SECRET_KEY="replace-with-a-secure-key" \
  -e DJANGO_DEBUG="true" \
  -e DB_ENGINE="django.db.backends.mysql" \
  -e DB_NAME="news_app_db" \
  -e DB_USER="news_user" \
  -e DB_PASSWORD="your_password" \
  -e DB_HOST="host.docker.internal" \
  -e DB_PORT="3306" \
  news-capstone
```

---

## Secrets & Credentials

**Never commit real credentials to Git.**

| Variable | Description |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret key — generate with `python -c "import secrets; print(secrets.token_hex(50))"` |
| `DB_PASSWORD` | MySQL password for `news_user` |
| `X_API_TOKEN` | X (Twitter) Bearer Token for posting announcements |

See `secrets.example.txt` for a full list of supported environment variables.

To obtain an X API token:
1. Go to https://developer.twitter.com/
2. Create a project and app
3. Generate a Bearer Token under the "Keys and Tokens" tab
4. Set it as the `X_API_TOKEN` environment variable

---

## Sphinx Documentation

The `docs/` folder contains the Sphinx documentation source. The generated
HTML is committed to the repository in `docs/_build/html/` for easy reviewer
access.

### To regenerate locally

```bash
# Install Sphinx (already in requirements.txt)
pip install sphinx sphinx-rtd-theme

# Navigate to the docs folder
cd docs

# Build HTML
make html       # macOS/Linux
make.bat html   # Windows
```

Open `docs/_build/html/index.html` in your browser.

---

## Running Tests

```bash
cd news_project
python manage.py test
```

The test suite covers the REST API endpoint (`/api/articles/`) with three
test cases: authentication requirement, reader subscription filtering, and
non-reader empty response.

---

## REST API

| Method | Endpoint | Auth Required | Description |
|---|---|---|---|
| `GET` | `/api/articles/` | Yes (Reader) | Returns approved articles for the reader's subscriptions |

**Example request:**
```bash
curl -u reader_username:password http://127.0.0.1:8000/api/articles/
```

---

## Git Branch Structure

| Branch | Purpose |
|---|---|
| `main` | Stable, merged code |
| `docs` | Added docstrings and generated Sphinx documentation |
| `container` | Added Dockerfile and Docker configuration |

---

## Pages

| URL | Description |
|---|---|
| `/` | Home (requires login) |
| `/register/` | Register a new account |
| `/login/` | Log in |
| `/news/articles/` | Browse articles |
| `/news/editor/articles/` | Editor review queue |
| `/api/articles/` | REST API |
| `/admin/` | Django admin panel |
