# imap2telegram

Imap2telegram watch imap email and send email to your telegram or [ntfy](https://ntfy.sh/)


## How to install in kubernetes

### Add helm repository

```bash
$ helm repo add imap https://oleksandr-mazur.github.io/helm/

$ helm repo update

$ helm install imap imap/imap2telegram-helm -f values.yaml
```

### values.yaml

```yaml
# required imap settings

imapHost: "127.0.0.1"
imapUser: "username"
imapPassword: "password"

# telegram settings, token and list of id users
telegramIDS: [32234]
telegramToken: ""

# ntfy settings
ntfyURL: ""
ntfyToken: ""
ntfyTags: "mag,eye_speech_bubble,mag_right"
ntfyPriority: "default"
ntfyMarkdown: "no"

resources:
   limits:
     cpu: 100m
     memory: 128Mi
   requests:
     cpu: 50m
     memory: 64Mi
```
