# Runbook: stuck or delayed agent jobs

## Trigger

`AgentJobQueueWaitHigh` fires, a customer reports a stalled build, or an ArgoCD rollout is healthy while agent runs do not progress.

## Triage

1. Identify the tenant, project, agent run, release, and first-seen timestamp from the alert labels and logs.
2. Check ArgoCD desired versus observed revision and inspect the resource tree. Do not assume a successful sync means workers are healthy.
3. Inspect Kubernetes events, pending pods, node pressure, resource quotas, image pulls, and scheduling constraints.
4. Query queue depth and oldest-message age. Compare the affected tenant with global service signals.
5. Correlate the run with deployment, trace, and cost events. Preserve the IDs and relevant log range in the incident record.

## Mitigation and recovery

- Scale only the constraining component after identifying it; avoid masking a dependency or quota failure with blanket worker scaling.
- Pause a faulty rollout through Git and let ArgoCD reconcile the known-good revision.
- Retry only idempotent jobs and record the attempt number. A retry must not duplicate a customer deployment or charge.
- When customer impact persists, assign an incident commander and communication owner; publish time-bounded updates.

## Follow-up

Record root cause, missing signal, owner, due date, and whether the event affected the error budget. Add a test or alert where it would have prevented recurrence.
