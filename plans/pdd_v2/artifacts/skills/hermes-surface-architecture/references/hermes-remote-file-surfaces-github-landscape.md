# Hermes remote file surfaces — GitHub landscape

Use this note when the task is to survey projects that expose remote files through Hermes, or that wrap a remote Hermes runtime with a file-oriented UI.

## Taxonomy

Split findings into three buckets. Do not mix them.

### 1. Hermes as remote file operator

Projects where Hermes directly manages or searches remote storage backends.

- `adnw-vinc/hermes-nextcloud`
  - Best direct match for file operations over remote storage.
  - Nextcloud over WebDAV plus notes/calendar/tasks/contacts.
  - File actions: list, upload, download, delete, move.
- `guanquntang/hermes-s3files-plugin`
  - Hermes plugin for AWS S3 Files mounted as local NFS.
  - Better framed as infrastructure-backed file access than as a polished file UI.
- `gregoryhorn/hermes-drive-index`
  - Google Drive retrieval/search layer for Hermes.
  - Not full file CRUD. Strong fit for discovery, snippets, and Drive links.

### 2. UI surfaces for a remote Hermes workspace

Projects where Hermes is the runtime/backend and the product surface exposes files from the Hermes host or workspace.

- `dodo-reach/hermes-desktop`
  - Native macOS SSH-first workspace.
  - Strong for remote host files, sessions, cron, skills, and terminal.
- `acegraphx/hermes-desktop-win`
  - Windows port of the SSH workspace pattern.
- `pyrate-llama/hermes-ui`
  - Web UI with file browser for the active Hermes workspace.
  - Better described as workspace-file browsing than cloud-storage integration.
- `fathah/hermes-desktop`
  - Broader desktop control plane with local or remote backend support.
  - Includes GUI management for profiles, sessions, tools, memory, schedules, and gateways.

### 3. Hermes as remote endpoint for another app

Projects where Hermes is exposed as a runtime/API endpoint, not as the file product itself.

- `Occa-Labs/adapter-hermes`
  - Adapter that drives a remote Hermes HTTP gateway.
  - Relevant when another system owns the UX and Hermes only supplies runtime execution.

## Query strategy

When searching GitHub in English, use both architecture terms and storage terms.

### Good repo-search queries

- `hermes nextcloud`
- `hermes s3`
- `hermes drive`
- `hermes desktop`
- `hermes ui`
- `"Hermes Agent" drive`
- `"Hermes Agent" WebDAV`
- `"Hermes Agent" filesystem`

### Why generic queries underperform

Queries such as `hermes remote file interface` or `hermes file manager` tend to return noise because many projects use Hermes as a codename unrelated to Hermes Agent.

Search becomes useful when you anchor it with one of these:
- a concrete backend: `nextcloud`, `s3`, `drive`, `webdav`
- a concrete surface: `desktop`, `ui`, `workspace`, `ssh`
- the exact phrase `"Hermes Agent"`

## Reporting pattern

When answering the user, report results under these headings:

1. Hermes as manager/operator of remote files
2. Interface for a remote Hermes workspace
3. Hermes as endpoint/runtime for another application

Then give a short verdict:
- best direct match for remote file management
- best desktop surface
- best web surface
- whether a universal multi-backend file manager around Hermes seems to exist yet

## Current practical verdict

As of the survey that produced this note:
- The ecosystem is stronger in backend-specific integrations plus remote workspace UIs.
- The ecosystem is weaker in universal, polished, multi-backend file management centered on Hermes.
- For product architecture, the clean separation is:
  - GUI owns the user experience
  - server owns auth, policy, and storage abstraction
  - Hermes acts as orchestrator/runtime behind that layer
