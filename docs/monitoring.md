# Monitor database with Percona Monitoring and Management (PMM)

{% include 'assets/fragments/monitor-db.txt' %}

## Check PMM Client health and status

A probe is a diagnostic mechanism in Kubernetes which helps determine whether a container is functioning correctly and whether it should continue to run, accept traffic, or be restarted.

PMM Client has the following probes:

* **Readiness probe** determines when a PMM Client is available and ready to accept traffic
* **Liveness probe** determines when to restart a PMM Client

To configure probes, use the `spec.pmm.readinessProbes` and `spec.pmm.livenessProbes` Custom Resource options.

