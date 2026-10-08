# Configure Operator environment variables

You can configure the Percona Operator for MySQL by setting environment variables on the Operator Deployment. This lets you tune Operator behavior without rebuilding images.

You can set environment variables in the following ways:

* For installations with `kubectl`, edit the Operator Deployment manifest (`deploy/bundle.yaml` / `deploy/operator.yaml` or `deploy/bundle-cw.yaml` / `deploy/operator-cw.yaml` in the [percona-server-mysql-operator :octicons-link-external-16:](https://github.com/percona/percona-server-mysql-operator) repository) before you apply it. You can also change the existing Deployment with `kubectl patch` or `kubectl edit`.
* For Helm installations, you can set environment variables through Helm values. Use the [ps-operator chart values :octicons-link-external-16:](https://github.com/percona/percona-helm-charts/tree/main/charts/ps-operator).
* For OpenShift installations that use OLM, configure environment variables in the Subscription.

## Available environment variables

### `LOG_STRUCTURED`

Controls whether Operator logs are structured (JSON) or plain text.

| Value type | Default | Example |
| ---------- | ------- | ------- |
| string     | `"false"` | `"true"` |

**Example configuration:**

```yaml
env:
  - name: LOG_STRUCTURED
    value: "true"
```

Structured logs work well with tools such as [jq :octicons-link-external-16:](https://stedolan.github.io/jq/). See also [Check the logs](debug-logs.md).

### `LOG_LEVEL`

Sets the verbosity of Operator logs.

| Value type | Default | Example |
| ---------- | ------- | ------- |
| string     | `INFO`  | `DEBUG` |

Valid values are:

* `VERBOSE` or `DEBUG` — Most verbose; `VERBOSE` also enables additional diagnostic output in some code paths.
* `ERROR` — Error messages only.
* `INFO` — Standard informational messages (default).
  
Any other value falls back to `INFO` with a message in the log.

**Example configuration:**

```yaml
env:
  - name: LOG_LEVEL
    value: DEBUG
```

### `WATCH_NAMESPACE`

Specifies which namespaces the Operator watches for `PerconaServerMySQL` and related custom resources.

By default, the value is set to the Operator’s own namespace from the metadata.namespace option via a downward API `fieldRef`:

```yaml
- name: WATCH_NAMESPACE
  valueFrom:
    fieldRef:
      apiVersion: v1
      fieldPath: metadata.namespace
```

| Value type | Default | Example |
| ---------- | ------- | ------- |
| string     | See below | `ns-one,ns-two` or `""` |

Accepted values:

* If set to a comma-separated list, the Operator watches those specific namespaces. The namespace list must include the namespace where the Operator itself is deployed. Use this approach for the [multi-namespace deployment](cluster-wide.md).
* If set to an empty string (`""`), the Operator watches all namespaces. 
  
When you deploy the Operator in cluster-wide mode, it should be associated with the appropriate ClusterRole.

**Example configuration:**

```yaml
env:
 - name: WATCH_NAMESPACE
   value: "mysql,mysql-dev,mysql-prod"
```

### `MAX_CONCURRENT_RECONCILES`

Sets the number of concurrent workers that reconcile `PerconaServerMySQL` and related custom resources in parallel. Useful when you manage multiple clusters with a single Operator. See [Configure concurrency for a cluster reconciliation](reconciliation-concurrency.md).

| Value type | Default | Example |
| ---------- | ------- | ------- |
| string     | `"1"`   | `"2"`   |

The value must be a positive integer. The Operator fails to start if the value is not a valid integer or is less than or equal to 0.

**Example configuration:**

```yaml
env:
  - name: MAX_CONCURRENT_RECONCILES
    value: "2"
```

### `DISABLE_TELEMETRY`

Disables anonymous telemetry data collection by the Operator. For what is collected when telemetry is enabled, see [Telemetry](telemetry.md).

| Value type | Default | Example |
| ---------- | ------- | ------- |
| string     | `"false"` | `"true"` |

**Example configuration:**

```yaml
env:
  - name: DISABLE_TELEMETRY
    value: "true"
```

### `PSO_LEADER_ELECTION_ENABLED`

Controls whether the Operator runs leader election. Leader election ensures only one Operator instance manages resources when multiple replicas run. Set this to `"false"` only when the Deployment has one replica.

When this variable is set, it overrides the `--leader-elect` container argument. When this variable is unset, the Operator uses that argument.

When you disable leader election, the Operator stops renewing the Lease. The existing Lease object stays in the namespace.

| Value type | Default | Example |
| ---------- | ------- | ------- |
| string     | `"true"` | `"false"` |

**Example configuration:**

```yaml
env:
  - name: PSO_LEADER_ELECTION_ENABLED
    value: "false"
```

### `PSO_LEADER_ELECTION_LEASE_NAME`

Sets the name of the Lease object that stores the leader lock. The Operator creates this Lease in the Operator namespace. The name must be a valid DNS subdomain.  Leave empty to use the default `08db2feb.percona.com`.

When you change the name, the Operator creates a new Lease. The previous Lease stays in the namespace.

| Value type | Default | Example |
| ---------- | ------- | ------- |
| string     | `"08db2feb.percona.com"` | `"my-lease"` |

**Example configuration:**

```yaml
env:
  - name: PSO_LEADER_ELECTION_LEASE_NAME
    value: "my-lease"
```

### `PSO_LEADER_ELECTION_LEASE_DURATION`

Sets how long another Operator replica waits after the last successful renewal before it takes leadership. Use a duration such as `60s` or `2m`. Increase this value when leader election fails because of high latency or limited resources.

The lease duration must be greater than the [renew deadline](#pso_leader_election_renew_deadline).

| Value type | Default | Example |
| ---------- | ------- | ------- |
| string     | `"60s"` | `"90s"` |

**Example configuration:**

```yaml
env:
  - name: PSO_LEADER_ELECTION_LEASE_DURATION
    value: "90s"
```

### `PSO_LEADER_ELECTION_RENEW_DEADLINE`

Sets how long the current leader retries renewing the Lease before it gives up leadership. Use a duration such as `40s`.

The renew deadline must be greater than the [retry period](#pso_leader_election_retry_period) multiplied by 1.2.

| Value type | Default | Example |
| ---------- | ------- | ------- |
| string     | `"40s"` | `"60s"` |

**Example configuration:**

```yaml
env:
  - name: PSO_LEADER_ELECTION_RENEW_DEADLINE
    value: "60s"
```

### `PSO_LEADER_ELECTION_RETRY_PERIOD`

Sets how long the Operator waits between leader election attempts. Use a duration such as `10s`.

| Value type | Default | Example |
| ---------- | ------- | ------- |
| string     | `"10s"` | `"15s"` |

**Example configuration:**

```yaml
env:
  - name: PSO_LEADER_ELECTION_RETRY_PERIOD
    value: "15s"
```

## Update environment variables

### Using `kubectl patch`

You can update environment variables in an existing Operator Deployment by applying a patch. To keep existing environment variables, you must specify the full list of them.

Here’s how to do it:

1. Get the current environment variables:
    
    ```bash
    kubectl get deployment percona-server-mysql-operator -n <operator-namespace> -o jsonpath='{.spec.template.spec.containers[0].env}' | jq
    ```

2. Update the deployment. This example command keeps downward API for `WATCH_NAMESPACE` and sets `LOG_LEVEL` to `DEBUG`:

    ```bash
    kubectl patch deployment percona-server-mysql-operator -n <operator-namespace> \
      --type='json' \
      -p='[{"op": "replace", "path": "/spec/template/spec/containers/0/env", "value": [
        {"name": "LOG_STRUCTURED", "value": "false"},
        {"name": "LOG_LEVEL", "value": "DEBUG"},
        {"name": "WATCH_NAMESPACE", "valueFrom": {"fieldRef": {"apiVersion": "v1",     "fieldPath": "metadata.namespace"}}},
        {"name": "MAX_CONCURRENT_RECONCILES", "value": "1"},
        {"name": "DISABLE_TELEMETRY", "value": "false"},
        {"name": "PSO_LEADER_ELECTION_ENABLED", "value": "true"},
        {"name": "PSO_LEADER_ELECTION_LEASE_NAME", "value": "08db2feb.percona.com"},
        {"name": "PSO_LEADER_ELECTION_LEASE_DURATION", "value": "60s"},
        {"name": "PSO_LEADER_ELECTION_RENEW_DEADLINE", "value": "40s"},
        {"name": "PSO_LEADER_ELECTION_RETRY_PERIOD", "value": "10s"}
      ]}]'
    ```

Adjust the list to match your current Deployment (for example cluster-wide `WATCH_NAMESPACE` with a string `value` instead of `valueFrom`). Starting with version 1.3.0, keep the `PSO_LEADER_ELECTION_*` entries in the list.

### Using `kubectl edit`

You can also edit the Deployment directly:

```bash
kubectl edit deployment percona-server-mysql-operator -n <operator-namespace>
```

Then modify the env section in the container specification, save, and exit. Kubernetes rolls out a new ReplicaSet for the Operator Pod.

After you change environment variables, the Operator Pod restarts with the new settings.
