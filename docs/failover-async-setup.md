# Configure and orchestrate zero-data-loss failover in async clusters

This page covers the setup and management of the zero-data-loss failover for clusters with [asynchronous replication](architecture.md#asynchronous-replication-tech-preview). For background on how the failover mechanism works and the explanation of the timeouts and Orchestrator behavior when timeout expires, see [About zero data loss failover](failover-async-about.md).

## Configure failover

Configure the `spec.orchestrator.failover` subsection in the Custom Resource. 

1. Set the following keys:
    
    * `timeout` - How long the cluster tries to recover transactions that exist only on the failed primary. The time covers every retry and starts at the first attempt for that primary.
    * `onTimeout` - What happens when timeout expires. The values are `Abort` and `ForceWithPossibleDataLoss`. See [Understand failover timeout and recovery policy](#understand-failover-timeout-and-recovery-policy) to learn more
    * `switchoverCatchUpTimeout` - How long a graceful switchover waits for the candidate to catch up before promoting it.

    ```yaml
    spec:
      orchestrator:
        failover:
          timeout: 6h
          onTimeout: Abort
          switchoverCatchUpTimeout: 5m
    ```

2. Apply the configuration:
    
    ```bash
    kubectl apply -f deploy/cr.yaml -n <namespace>
    ```

## See whether a failover is blocked

The Operator reports whether the cluster currently has a writable primary in the `AsyncFailoverBlocked` condition:

```bash
kubectl get ps <cluster-name> -n <namespace> \
  -o jsonpath='{range .status.conditions[?(@.type=="AsyncFailoverBlocked")]}{.status}{": "}{.reason}{"\n"}{end}'
```

A `status: "True"` with `reason: NoWritablePrimary` means writes are currently blocked. See [Conditions](cr-statuses.md#conditions) and [Events](cr-statuses.md#events) for the full list of condition and event reasons this feature adds.

The Operator leaves the condition unchanged when:

* Cluster has one MySQL Pod
* Orchestrator Pod is not ready, or Orchestrator cannot resolve the cluster or its primary
* Planned switchover holds the primary in downtime

The cluster also records these events:

| Reason | Type | When |
| --- | --- | --- |
| `FailoverWaiting` | Normal | The first attempt for a primary. The cluster has no writable primary until recovery finishes, for up to `timeout`. The event names the `onTimeout` policy. |
| `FailoverBlocked` | Warning | `timeout` expired and `onTimeout` is `Abort`. |
| `FailoverForced` | Warning | `timeout` expired and `onTimeout` is `ForceWithPossibleDataLoss`, or the force-promotion annotation was handled. |
| `FailoverFailed` | Warning | Orchestrator gave up on the recovery. |

Orchestrator retries a blocked recovery every few seconds. After one `FailoverWaiting`, `FailoverBlocked`, or `FailoverFailed` event for a primary, the same event stays quiet for five minutes. `FailoverForced` is recorded each time.

## Force a promotion

When the old primary's binary logs cannot be recovered, and you accept losing the transactions that never reached a replica, annotate the cluster:

```bash
kubectl annotate ps <cluster-name> -n <namespace> \
  percona.com/force-promote-with-possible-data-loss=<value>
```

`<value>` is one of the following:

* Pod name, such as `cluster1-mysql-2`, names the replica to promote. Orchestrator has to know that Pod as a member of this cluster.
* `true` leaves the choice to the Operator. It uses the same ranking as a failover.

A forced promotion does not fetch binary logs. The failover hook treats it as a planned takeover and returns without salvaging.

!!! warning "Writable primary"

    The Operator refuses this annotation while the cluster has a writable primary. A forced promotion does not stop that primary or point it at the new one. If it still accepts writes, the promoted replica misses those writes and the old primary keeps its own data.

The Operator also refuses the request when Orchestrator cannot resolve the cluster or its primary.

The Operator removes the annotation after it handles the request. That is when:

* the replica is promoted, 
* the request fails or is refused, or 
* the candidate is already the primary. 
  
When no Orchestrator Pod is ready or when Orchestrator is still busy recovering the failed primary, the annotation stays and the Operator tries again on the next reconcile.