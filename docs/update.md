# Upgrade Database and Operator

You can upgrade Percona Operator for MySQL based on Percona
Server for MySQL to newer versions. 

The upgrade process consists of these steps:

* upgrade the Operator;
* update the Custom Resource Definition version,
* upgrade the database (Percona Server for MySQL).

## Update scenarios

You can either upgrade both the Operator and the database, or you can upgrade only the database. To decide which scenario to choose, read on.

### Full upgrade (CRD, Operator, and the database)

When to use this scenario:

* The new Operator version has changes that are required for new features of the database to work
* The Operator has new features or fixes that enhance automation and management.
* Compatibility improvements between the Operator and the database require synchronized updates.

When going on with this scenario, make sure to test it in a staging or testing environment first. Upgrading the Operator may cause performance degradation.

### Upgrade only the database

When to use this scenario:

* The new version of the database has new features or fixes that are not related to the Operator or other components of your infrastructure
* You have updated the Operator earlier and now want to proceed with the database update.

When choosing this scenario, consider the following:

* Check that the current Operator version supports the new database version.
* Some features may require an Operator upgrade later for full functionality.

## Update strategies

The Operator supports the *Smart Update* strategy. This is the automated way to update the database cluster. The Operator controls how objects are updated. It restarts Pods in a specific order, with the primary instance updated last to avoid connection issues until the whole cluster is updated to the new settings.

This update method applies during database upgrades and when making changes like updating a ConfigMap, rotating passwords, or changing resource values. 

