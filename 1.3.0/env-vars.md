> For the complete documentation index, see [llms.txt](https://docs.percona.com/percona-operator-for-mysql/1.3.0/llms.txt).

# Configure environment variables

You can configure environment variables in Percona Operator for MySQL based on Percona Server for MySQL for the following purposes:

1. **[Configure Operator environment variables](https://docs.percona.com/percona-operator-for-mysql/1.3.0/env-vars-operator.md)** — Control the Operator’s behavior, such as logging, telemetry, leader election, and which namespaces the Operator watches. You set these for the Operator Deployment.
1. **[Define environment variables for cluster components](https://docs.percona.com/percona-operator-for-mysql/1.3.0/env-vars-custom.md)** — Set variables for database and proxy Pods through the Custom Resource (`deploy/cr.yaml`): use **supported tuning names** (for example bootstrap or HAProxy timeouts) or **arbitrary custom** names, via `env` / `envFrom` and optional ConfigMaps or Secrets.

## When to use environment variables

| Type                                    | Use cases                                                                                                                                                                                                                                         |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Operator environment variables          | - Control logging for debugging and log aggregation. - Manage [telemetry](https://docs.percona.com/percona-operator-for-mysql/1.3.0/telemetry.md). - Configure the namespaces for the Operator to watch. - Configure leader election timing.      |
| Cluster component environment variables | - Use documented names to tune bootstrap, HAProxy, Router, Orchestrator, and backups. - Pass any extra variables your containers need (for example `TZ`). - All of this is configured in the **Custom Resource**, not on the Operator Deployment. |

For field-level details, see [Custom Resource options](https://docs.percona.com/percona-operator-for-mysql/1.3.0/operator.md).
