# Delete the unneeded backup

Manual deleting of a previously saved backup requires not more than the backup
name. This name can be taken from the list of available backups returned
by the following command:

```bash
kubectl get ps-backup
```

When the name is known, backup can be deleted as follows:

```bash
kubectl delete ps-backup/<backup-name>
```