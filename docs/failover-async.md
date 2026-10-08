# Zero data loss failover in async clusters

This page applies to clusters with [asynchronous replication](architecture.md#asynchronous-replication-tech-preview), where Orchestrator manages the replication topology. 

## Overview 

In an async cluster, replication runs with some lag. This lag means a transaction has already reached a replica's relay log and waits to be applied.  

If the primary goes down as a result of an out-of-memory kill or a hardware failure and it hasn't transmitted a transaction to any replica before that, that transaction exists only in that primary's binary log. Promoting a replica at that point loses this data.

To ensure no data is lost during a failover, the Operator and Orchestrator split the failover process into these stages: 

1. **[Fetch the transactions still on the failed primary](#fetch-the-transactions-from-the-primarys-binary-log).** The candidate replica reads them from the old primary's binary logs.
2. **[Apply the transactions to the candidate and wait for it to catch up](#apply-the-binary-logs-on-the-candidate-replica).** The candidate then has everything the old primary had finished writing.
3. **[Promote the candidate](#promote-the-candidate).**

Until the candidate is promoted, or until the failover timeout expires, the cluster has no writable primary. The default timeout is `6h`. You set that limit when you [Configure failover](failover-async-configure.md#configure-failover). What happens while the cluster waits and when the timeout runs out is covered in [Understand failover timeout and recovery policy](#understand-failover-timeout-and-recovery-policy).

Orchestrator drives the failover stages through its failover hooks. The Operator's role is to configure the mechanism through the Custom Resource, oversee it and surface its outcome through the cluster's conditions and events.

## Requirements

* The Operator version 1.3.0 and higher
* The MySQL cluster that:

    * Uses asynchronous replication with Orchestrator
    * Uses `spec.crVersion` `1.3.0` or later

On an older `crVersion`, the Operator accepts `spec.orchestrator.failover` but does not apply it. Setting that block on a group replication cluster fails validation. A cluster of one MySQL Pod has no replica to promote.

The binary log and relay log settings a zero data loss failover depends on are described in [Known limitations](#known-limitations).

## How failover works

Let's have a closer look at the failover stages

### Fetch the transactions from the primary's binary log

The `xtrabackup` sidecar in every MySQL Pod runs an HTTP server that controls backups. A replica to be promoted (the candidate) connects to this server on the `/failover/stream:6450` endpoint  to fetch the binary logs it does not have yet.

The candidate authenticates as the [`operator`](users.md#system-users) user and reads whatever transactions the old primary never replicated directly from its binary logs, starting from the latest position the replica I/O thread has received from the primary. The position is determined by the values from `Source_Log_File` and `Read_Source_Log_Pos`. 

The sidecar returns one tar stream that includes everything from the requested position to the last log. The candidate extracts the archive into a staging directory. The default path is `/var/lib/mysql/source-logs`.

#### If the primary Pod is unreachable

To fetch binary logs, the old primary Pod needs to be reachable over the network. `mysqld` on that Pod can be down. The `xtrabackup` sidecar serves the binary logs over HTTP.

When the Pod can't be scheduled, or the candidate can't reach it, a fetch attempt fails. Orchestrator retries repeatedly until the [failover timeout](#understand-failover-timeout-and-recovery-policy) is reached. 

An attempt stops at either of these limits:

* Orchestrator waits up to two minutes for the source Pod to exist and receive an IP address.
* Streaming stops when the source sends no data for two minutes.

The second limit covers sidecar startup, the response headers, and each read of the body. A transfer that keeps sending data runs to completion.

### Apply the binary logs on the candidate replica

The candidate adds the binary logs it just fetched to its relay log, then waits until they are applied.

The candidate takes these steps:

1. Stops replication, so nothing new arrives while the logs are added.
2. Closes the relay log it was writing. MySQL opens a new relay log, and the closed one receives the fetched logs.
3. Adds the fetched binary logs to the end of that closed relay log.
4. Starts applying those events and waits until every one of them is applied.

The replication process that normally receives events from a primary remains stopped, since there is no primary available until the candidate is promoted. Once the candidate finishes applying the fetched events, it contains all the transactions that the old primary had stored in its binary log.

A crash can leave a partial event at the end of the last binary log. That fragment is left out. The primary never finished writing it, and applying it would stop replication on the candidate.

When the candidate already has everything the primary wrote, nothing is added and the candidate moves on.

### Promote the candidate

After the candidate has caught up, Orchestrator promotes it. The candidate becomes the primary and starts accepting writes. The other replicas replicate from it.

Orchestrator chooses which replica to promote. It prefers a replica with no problems reported, then the one that has applied the most transactions. When two replicas are equal, the one with the lower Pod name is chosen.

A candidate that fails its readiness probe during failover is expected. Orchestrator can still reach that Pod and promote it.

A planned switchover does not salvage binary logs. The primary is alive, so the failover hook returns without fetching them. The switchover waits for the candidate to catch up, then promotes it. The time to wait is defined with the [`switchoverCatchUpTimeout`](failover-async-configure.md#configure-failover) Custom Resource option.

### If the old primary comes back

Orchestrator keeps checking whether the old primary is back. The check runs before the candidate is changed, again while the candidate applies the recovered transactions, and once more just before promotion. A primary that comes back during that wait stops the promotion, even when applying has just finished.

The old primary counts as back when both of these are true:

* Accepts connections
* Holds every transaction the candidate already has

If the candidate has transactions the old primary no longer has, the check fails and promotion continues. That is what keeps those transactions.

A Pod that has only restarted is still read-only. Orchestrator  counts it as back when it accepts connections and holds every transaction the candidate has. Orchestrator stops the failover only after two successful checks in a row, so one brief response does not cancel it.

When the old primary is back, Orchestrator aborts the failover and promotes nothing. It then makes that primary writable. Promoting the candidate as well would leave two Pods accepting writes. The candidate starts replicating from the old primary again. Events already added to its relay log stay there and keep being applied. The candidate also requests that same range from the primary, and MySQL skips transactions it has already applied.

Orchestrator ends the failover. 

When the old primary's Pod is gone, Orchestrator skips the check and the promotion continues.

 [Configure failover](failover-async-configure.md#configure-failover):

* **`Abort`** (default) Orchestrator stops the recovery, and every Pod stays read-only. Orchestrator keeps retrying, and each retry stops immediately. The cluster stays read-only until you [force a promotion](failover-async-configure.md#force-a-promotion). See the event table in [See whether a failover is blocked](failover-async-configure.md#see-whether-a-failover-is-blocked) for what the cluster records.

* **`ForceWithPossibleDataLoss`** makes Orchestrator pick a candidate and skip the binary log fetch. It still checks whether the old primary is back. When that primary accepts connections and holds every transaction the candidate has, nothing is promoted, and Orchestrator makes the primary writable. Otherwise Orchestrator promotes the candidate. Transactions that never left the old primary are lost. When the primary has no replicas, nothing is promoted. See the event table in [See whether a failover is blocked](failover-async-configure.md#see-whether-a-failover-is-blocked) for what gets recorded.

## Known limitations

Zero-data-loss recovery depends on durability that the Operator doesn't enforce:

* **Durable commits on the primary** This assumes `sync_binlog=1` and `innodb_flush_log_at_trx_commit=1` on every Pod. These are MySQL's defaults, and the Operator does not change them. Relax either one, and a crashed primary can lose transactions it already acknowledged to clients before they reached disk. No recovery step brings those back.

* **Durable relay logs on the candidate**. The Operator doesn't set relay log durability options either, so MySQL's defaults apply (`sync_relay_log=10000` and `relay_log_recovery=ON`). A candidate that crashes mid-recovery can lose relay log events it already received, including the ones fetched from the old primary. The next failover attempt reads that position and fetches the missing range again, as long as the old primary's binary logs are still available. This costs a retry.

* **The old primary's binary logs must still exist.** If they were already purged or expired, every recovery attempt fails the same way until `orchestrator.failover.timeout` runs out and [`onTimeout`](#understand-failover-timeout-and-recovery-policy) applies. Nothing can recover those transactions.

* **The old primary's data volume must still exist.** If it's gone, the transactions it alone held are gone too. The only way forward is [`onTimeout`](#understand-failover-timeout-and-recovery-policy) or the [force-promote annotation](failover-async-configure.md#force-a-promotion).
* **Binlog encryption with [data-at-rest-encryption](encryption.md) is not supported**

Starting at `crVersion` 1.3.0, the Operator also pins several Orchestrator settings that this mechanism depends on and silently ignores any conflicting value in [`orchestrator.configuration`](operator.md#orchestratorconfiguration) — see that field's reference entry for the current list.
