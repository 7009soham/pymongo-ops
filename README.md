# pymongo-ops

A FastAPI application backed by MongoDB (via **pymongo**), containerised with Docker, and deployed to Amazon EKS. The project demonstrates a GitOps-style CI/CD pipeline where **CI is fully automated** (GitHub Actions → Amazon ECR → GitOps repo update) and **CD is intentionally manual** (Argo CD → EKS, with Karpenter managing node provisioning).

---

## Table of Contents

- [Project Description](#project-description)
- [Architecture Overview](#architecture-overview)
- [API Endpoints](#api-endpoints)
- [CI/CD Approach](#cicd-approach)
  - [Continuous Integration (automated)](#continuous-integration-automated)
  - [Continuous Deployment (manual)](#continuous-deployment-manual)
- [Developer Workflow](#developer-workflow)
  - [Running CI](#running-ci)
  - [Workflow Files](#workflow-files)
  - [Required Secrets](#required-secrets)
- [Local Development](#local-development)

---

## Project Description

**pymongo-ops** is a lightweight REST API built with [FastAPI](https://fastapi.tiangolo.com/) that performs CRUD operations against a MongoDB collection. It exposes endpoints for inserting users and querying them by name, age, or role, plus a health-check and a database-connectivity check.

The repository also serves as a reference implementation for a GitOps-style pipeline: every push to `main` builds and pushes a new Docker image and automatically updates the image tag in a separate GitOps deploy repository, while actual cluster deployments remain under human control via Argo CD.

---

## Architecture Overview

| Layer | Technology |
|---|---|
| Application | FastAPI + pymongo (Python 3.9) |
| Containerisation | Docker (image tagged with Git SHA) |
| Image Registry | Amazon ECR |
| Orchestration | Amazon EKS |
| Node Provisioning | Karpenter |
| GitOps Manifests | Separate deploy repo (`pymongo-ops-deploy`) with Kustomize |
| Deployment Engine | Argo CD (manual sync) |
| CI Automation | GitHub Actions |

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Root – returns a welcome message |
| `GET` | `/health` | Health check – returns `{"Status": "healthy"}` |
| `GET` | `/db-check` | Verifies MongoDB connectivity |
| `POST` | `/insert` | Insert a user (`{"name": str, "age": int, "role": str}`) |
| `GET` | `/users` | Return all users |
| `GET` | `/find/name?name=<value>` | Find users by exact name |
| `GET` | `/find/role?role=<value>` | Find users by exact role |
| `GET` | `/find/age?age=<value>` | Find users with age **greater than** the given value |

Interactive API docs are available at `http://localhost:8000/docs` when running locally.

---

## CI/CD Approach

### Continuous Integration (automated)

Every push to the `main` branch triggers the CI pipeline defined in `.github/workflows/ci.yml`. The pipeline:

1. Checks out the source code.
2. Authenticates to AWS using repository secrets.
3. Logs in to Amazon ECR.
4. Builds a Docker image tagged with the commit SHA (`ECR_URI:<git-sha>`).
5. Pushes the image to ECR.
6. Clones the GitOps deploy repository (`pymongo-ops-deploy`) and updates `k8s/kustomization.yaml` with the new image tag, then commits and pushes the change.

CI does **not** trigger a cluster deployment — the Argo CD sync step is always manual.

### Continuous Deployment (manual)

Deployments are performed manually using **Argo CD**:

1. Argo CD is installed inside the EKS cluster and pointed at the `pymongo-ops-deploy` GitOps repository.
2. **Auto-sync is disabled** — Argo CD will detect drift (OutOfSync) but will not apply changes without human approval.
3. After CI updates the GitOps repo, the developer opens the Argo CD UI (or runs `argocd app sync <app-name>` via CLI) and clicks **Sync**.
4. Karpenter automatically provisions any additional nodes required by newly scheduled pods — no manual node management is needed.

> ⚠️ **Do not enable Argo CD auto-sync** unless you intentionally want every manifest commit to be deployed without a manual gate.

---

## Developer Workflow

### Running CI

CI runs automatically on every push to `main`:

```bash
git add .
git commit -m "your change"
git push origin main
```

Monitor the run in the **Actions** tab of this repository.

### Workflow Files

| File | Purpose |
|---|---|
| `.github/workflows/ci.yml` | Builds the Docker image, pushes it to ECR, and updates the image tag in the GitOps deploy repo |

### Required Secrets

The following secrets must be configured in the repository settings (**Settings → Secrets and variables → Actions**):

| Secret | Description |
|---|---|
| `AWS_ACCESS_KEY_ID` | AWS IAM access key with ECR push permissions |
| `AWS_SECRET_ACCESS_KEY` | Corresponding AWS IAM secret key |
| `AWS_REGION` | AWS region where ECR is hosted (e.g. `ap-south-1`) |
| `ECR_URI` | Full ECR repository URI (e.g. `123456789.dkr.ecr.ap-south-1.amazonaws.com/ci-cd-app`) |
| `GITOPS_REPO_TOKEN` | GitHub personal access token with write access to `pymongo-ops-deploy` |

---

## Local Development

A `docker-compose.yaml` is included for spinning up the application and a local MongoDB instance together.

```bash
# Start the stack (app on port 8000, MongoDB on port 27017)
docker compose up --build
```

The app reads `MONGO_URI` from the `.env` file at startup (via `python-dotenv`). For local development, point it at the bundled MongoDB container:

```
# .env
MONGO_URI=mongodb://mongodb:27017
```

| Variable | Description |
|---|---|
| `MONGO_URI` | MongoDB connection string used by the application |
