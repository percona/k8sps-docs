# Configure environment variables

You can configure environment variables in Percona Operator for MySQL based on Percona Server for MySQL for the following purposes:

1. **[Configure Operator environment variables](env-vars-operator.md)** — Control the Operator’s behavior, such as logging, telemetry, and which namespaces the Operator watches. You set these on the Operator Deployment (`deploy/operator.yaml` or equivalent).
2. **[Define environment variables for cluster components](env-vars-custom.md)** — Set variables for database and proxy Pods through the Custom Resource (`deploy/cr.yaml`): use **supported tuning names** (for example bootstrap or HAProxy timeouts) or **arbitrary custom** names, via `env` / `envFrom` and optional ConfigMaps or Secrets.

## When to use environment variables

| Type | Use cases |
| ---- | --------- |
| Operator environment variables | - Control logging for debugging and log aggregation. <br> - Manage [telemetry](telemetry.md). <br> - Configure the namespaces for the Operator to watch. |
| Cluster component environment variables | - Use documented names to tune bootstrap, HAProxy, Router, Orchestrator, and backups. <br> - Pass any extra variables your containers need (for example `TZ`). <br> - All of this is configured in the **Custom Resource**, not on the Operator Deployment. |

For field-level details, see [Custom Resource options](operator.md).
