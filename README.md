# Agent Platform Operations Reference

> A technical application artifact for Emergent's Software Engineer - Infrastructure role. It demonstrates an operable contract for running AI-agent jobs on Kubernetes: GitOps delivery, workload lifecycle signals, cost attribution, and incident-ready runbooks.

## Why this project

Emergent's agents do more than serve requests: they schedule work, provision environments, deploy applications, and must be traceable and cost-aware at scale. That means a platform team needs a common workload contract - not a collection of dashboards assembled after something fails.

This reference turns each agent run into an observable unit of work with an owner, environment, version, lifecycle state, and cost dimensions. It is deliberately small enough to review, test, and extend.

I am Rahul H Bhatia, a platform engineer with production AWS/GCP, Kubernetes, Terraform, GitOps, identity, and observability experience. My work includes reusable infrastructure modules that reduced service onboarding to under two hours, private-by-default cloud architecture, EKS cost and reliability improvements, and production incident ownership. This repository is an application artifact, not a claim that it is deployed at Emergent today.

## Role alignment

| Emergent need | Reference implementation |
| --- | --- |
| Kubernetes workloads and GitOps | An `AgentJob` workload contract and ArgoCD Application manifest make versioned deployment intent explicit. |
| Agent scheduling and trajectory tracking | Lifecycle labels, terminal states, attempt count, and a stable `agent_run_id` make runs queryable. |
| Cost attribution | A dependency-free Python CLI aggregates CPU, memory, and token cost by tenant, project, and run. |
| Grafana, Prometheus, Loki | ServiceMonitor and Prometheus alert rules define scrape and alert conventions; runbooks connect alerts to actions. |
| Incident response | Runbooks distinguish failing rollouts, stuck jobs, and cost anomalies with evidence-first triage. |
| Cloud-native delivery | Kustomize-ready manifests and CI validation keep operational configuration reviewable. |

## Architecture

```text
Git pull request
  -> ArgoCD sync
      -> AgentJob workload contract
          -> agent executor / ephemeral environment
              -> metrics, logs, traces, lifecycle events
                  -> Prometheus + Grafana + Loki
                      -> SLO alerts and incident runbooks

Lifecycle/cost events -> tools/cost_attribution.py -> tenant/project/run reports
```

## Repository map

```text
k8s/agent-job.yaml            Example workload contract for an agent run
k8s/argocd-application.yaml   GitOps deployment intent
k8s/observability.yaml         Prometheus scrape and alert policy
tools/cost_attribution.py      Testable event-to-cost aggregation CLI
tests/test_cost_attribution.py Unit tests for attribution correctness
runbooks/                      Rollout, stuck-job, and cost-anomaly response
```

## Run locally

```bash
python3 -m unittest discover -s tests -v
python3 tools/cost_attribution.py examples/events.json
```

The cost tool accepts JSON events such as:

```json
{
  "agent_run_id": "run-123",
  "tenant_id": "acme",
  "project_id": "invoice-parser",
  "cpu_seconds": 41.2,
  "memory_gib_seconds": 88.0,
  "input_tokens": 1200,
  "output_tokens": 350
}
```

It deliberately uses configurable unit prices rather than pretending cloud or model costs are universal. In production, the event source would be the scheduler/worker control plane, not hand-authored JSON.

## Operating model

### 1. Treat agent runs as first-class operations

Every run gets a stable ID, tenant and project dimensions, an application version, attempt number, and lifecycle state. These fields belong in metrics, structured logs, traces, and cost events. An alert without this context is harder to route and impossible to price.

### 2. Make rollout failure cheap to diagnose

ArgoCD sync health, Kubernetes readiness, and application-level success should be separate signals. A green sync is not proof that an agent worker is consuming jobs. The rollout runbook starts with the desired/observed Git revision, then checks resource trees, events, logs, and workload metrics.

### 3. Use SLOs to balance speed and reliability

Initial service-level indicators should include agent-run success rate, queue wait duration, execution latency, failed environment provisioning, and cost per successful run. Error budgets should slow risky release cohorts before availability becomes an incident.

### 4. Make cost actionable

Cost attribution must be joinable to customer value: tenant, project, feature/model, and run. The correct response to a cost anomaly is not only a budget alert - it is a traceable route to the workload, release, and request pattern responsible.

## What I would extend next

1. A Kubernetes controller built with controller-runtime or Kubebuilder to reconcile `AgentJob` state and enforce retries, quotas, and cleanup.
2. OpenTelemetry spans from request to environment provision, deployment, and execution.
3. Queue-depth autoscaling and per-tenant concurrency controls.
4. Postgres-backed run metadata with retention, backup/restore drills, and operator dashboards.
5. Policy checks for image provenance, secrets, egress, and ephemeral environment TTLs.

## Candidate links

- [LinkedIn](https://www.linkedin.com/in/rahul-h-bhatia/)
- [Portfolio](https://rahulhbhatia.vercel.app)
- [Credly](https://www.credly.com/users/rahul-h-bhatia/badges)
