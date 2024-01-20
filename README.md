# Hetzner Dynamic DNS

A Python script for updating a DNS A record to be the running host's public IPv4 address. Run regularly, e.g., as a
Kubernetes CronJob.

To-Do: AAAA/IPv6 support.

## Sample Kubernetes CronJob

```yaml
---
apiVersion: batch/v1
kind: CronJob
metadata:
  name: dyndns-hetzner
spec:
  schedule: "*/5 * * * *"
  jobTemplate:
    spec:
      template:
        spec:
          containers:
            - name: dyndns-hetzner
              image: ghcr.io/sschaeffner/hetzner-dyndns:<TODO-PUT-IMAGE-TAG-HERE>
              imagePullPolicy: IfNotPresent
              env:
                - name: TOKEN
                  valueFrom:
                    secretKeyRef:
                      name: hetzner-dns-secret
                      key: api-key
                - name: ZONE_NAME
                  value: example.com
                - name: DOMAIN
                  value: dyn.example.com
                - name: TTL
                  value: "300" # 5 minutes
          restartPolicy: Never
---
apiVersion: v1
kind: Secret
metadata:
  name: hetzner-dns-secret
type: Opaque
stringData:
  api-key: "TODO-PUT-YOUR-HETZNER-DNS-API-KEY-HERE"
```
