## Delete the unneeded backup

Manual deleting of a previously saved backup requires not more than the backup
name. This name can be taken from the list of available backups returned
by the following command:

```{.bash data-prompt="$"}
$ kubectl get ps-backup
```

When the name is known, backup can be deleted as follows:

```{.bash data-prompt="$"}
$ kubectl delete ps-backup/<backup-name>
```