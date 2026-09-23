# Cloudflare Scheduler

This folder contains the external scheduler for JxJ Stock Watcher.

The Worker runs every 5 minutes and sends a GitHub `repository_dispatch` event:

```
event_type: jxj-stock-check
```

GitHub then runs:

```
.github/workflows/scheduled-monitor.yml
```

## Required secret

The Worker needs one secret:

```
GITHUB_TOKEN
```

Use a fine-grained GitHub personal access token limited to:

- Repository: `cutecubeandy/JxJ_Stock_Watcher`
- Repository permission: Contents — Read and write

Do not commit the token into this repository.

## Expected GitHub Actions log

When the external scheduler triggers correctly, the first step should show:

```
Triggered by: repository_dispatch
```
