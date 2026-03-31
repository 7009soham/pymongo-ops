# pymongo-ops

A FastAPI application backed by MongoDB (via **pymongo**), containerised with Docker and deployed to Amazon EKS. The project demonstrates a complete CI/CD pipeline where **CI is fully automated** (GitHub Actions → Amazon ECR) and **CD is intentionally manual** (Argo CD → EKS, with Karpenter managing node provisioning).

---
updaeted
## Table of Contents

- [Project Description](#project-description)
- [Architecture Overview](#architecture-overview)
- [CI/CD Approach](#cicd-approach)
  - [Continuous Integration (automated)](#continuous-integration-automated)
  - [Continuous Deployment (manual)](#continuous-deployment-manual)
- [Developer Workflow](#developer-workflow)
  - [Running CI](#running-ci)
  - [Promoting an Image for Deployment](#promoting-an-image-for-deployment)
  - [Workflow Files](#workflow-files)
- [Local Development](#local-development)
- [Contributing](#contributing)
- [Contact](#contact)

---

## Project Description

**pymongo-ops** is a lightweight REST API built with [FastAPI](https://fastapi.tiangolo.com/) that performs CRUD operations against a MongoDB collection. It exposes endpoints for inserting users and querying them by name, age, or role, plus a health-check and database-connectivity check.

The repository also serves as a reference implementation for a GitOps-style pipeline where image builds are automated but production deployments remain under human control.

---

## Architecture Overview

| Layer | Technology |
|---|---|
| Application | FastAPI + pymongo (Python 3.9) |
| Containerisation | Docker (image tagged with Git SHA) |
| Image Registry | Amazon ECR |
| Orchestration | Amazon EKS |
| Node Provisioning | Karpenter |
| Deployment Engine | Argo CD (manual sync) |
| CI Automation | GitHub Actions |

---

## CI/CD Approach

### Continuous Integration (automated)

Every push to the `main` branch triggers the CI pipeline defined in `.github/workflows/ci.yml`. The pipeline:

1. Checks out the source code.
2. Authenticates to AWS using repository secrets (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION`).
3. Logs in to Amazon ECR.
4. Builds a Docker image tagged with the commit SHA (`ECR_URI:<git-sha>`).
5. Pushes the image to ECR.

CI does **not** trigger a deployment. The cluster state is never changed automatically.

### Continuous Deployment (manual)

Deployments are performed manually using **Argo CD**:

1. Argo CD is installed inside the EKS cluster and pointed at this repository (or a dedicated deploy/manifests repo).
2. **Auto-sync is disabled** — Argo CD will detect drift (OutOfSync) but will not apply changes without human approval.
3. To deploy a new image a developer:
   - Updates `deployment.yaml` (or the relevant Helm/Kustomize values file) with the new image tag (`ECR_URI:<git-sha>`).
   - Commits and pushes the manifest change.
   - Opens the Argo CD UI (or uses `argocd app sync <app-name>` via CLI) and clicks **Sync**.
4. Karpenter reacts to any newly scheduled pods that require additional capacity and provisions the appropriate nodes automatically — no manual node management is needed.

> ⚠️ **Do not enable Argo CD auto-sync** unless you intentionally want every manifest commit to be deployed without a manual gate.

---

## Developer Workflow

### Running CI

CI runs automatically on every push to `main`. To trigger it:

```bash
git add .
git commit -m "your change"
git push origin main
```

Monitor the run in the **Actions** tab of this repository.

### Promoting an Image for Deployment

1. Find the Git SHA of the image you want to deploy (from the ECR console or the CI run summary).
2. Update the image tag in `deployment.yaml`:
   ```yaml
   image: <your-ecr-uri>:<git-sha>
   ```
3. Commit and push the change:
   ```bash
   git add deployment.yaml
   git commit -m "chore: promote image <git-sha> to production"
   git push origin main
   ```
4. In the Argo CD UI, wait for the application to show **OutOfSync**, then click **Sync** (or run `argocd app sync <app-name>`).

### Workflow Files

| File | Purpose |
|---|---|
| `.github/workflows/ci.yml` | Builds the Docker image and pushes it to ECR on every push to `main` |

---

## Local Development

> _TODO: add local development instructions here._

A `docker-compose.yaml` is included in the repository for spinning up the application and a MongoDB instance locally.

```bash
# Start the stack
docker compose up --build

# The API will be available at http://localhost:8000
# Interactive docs: http://localhost:8000/docs
```

Required environment variables (see `.env`):

| Variable | Description |
|---|---|
| `MONGO_URI` | MongoDB connection string |

---

## Contributing

> _TODO: add contributing guidelines here (branch strategy, PR template, code style, etc.)._

---

## Contact

> _TODO: add maintainer contact information or link to project communication channels here._
