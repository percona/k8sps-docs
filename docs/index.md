# Percona Operator for MySQL based on Percona Server for MySQL

Kubernetes have added a way to
manage containerized systems, including database clusters. This management is
achieved by controllers, declared in configuration files. These controllers
provide automation with the ability to create objects, such as a container or a
group of containers called Pods, to listen for a specific event and then
perform a task.

This automation adds a level of complexity to the container-based architecture
and stateful applications, such as a database. A Kubernetes Operator is a
special type of controller introduced to simplify complex deployments. The
Operator extends the Kubernetes API with custom resources.

[Percona Server for MySQL](https://www.percona.com/doc/percona-server/LATEST/index.html)
is a free, fully compatible, enhanced, and open source drop-in replacement for
any MySQL database. It provides superior performance, scalability, and
instrumentation.

!!! note

    Version {{ release }} of the [Percona Operator for MySQL](https://github.com/percona/percona-server-mysql-operator) is **a tech preview release** and it is **not recommended for production environments**. **As of today, we recommend using** [Percona Operator for MySQL based on Percona XtraDB Cluster](https://www.percona.com/doc/kubernetes-operator-for-pxc/index.html), which is production-ready and contains everything you need to quickly and consistently deploy and scale MySQL clusters in a Kubernetes-based environment, on-premises or in the cloud.


