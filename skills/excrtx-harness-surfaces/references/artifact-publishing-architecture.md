# Artifact publishing architecture for Hermes

Session context: user asked for an organic way for Hermes to deliver final artifacts (docs, PDFs, spreadsheets, ZIPs, HTML) to users, including remote gateway/sandbox scenarios, while using GitHub for code repositories.

## Durable lesson

Treat final artifact delivery as a first-class Hermes surface, not as an ad hoc `MEDIA:/path` convention. Local paths are insufficient once Hermes runs behind a gateway, remote terminal backend, Docker/SSH/Modal sandbox, or any environment where the gateway cannot read the producing filesystem.

## Recommended contract

Expose a single tool/MCP capability:

```json
publish_artifact(path, kind, title, audience, ttl, visibility) -> ArtifactReceipt
```

Representative receipt:

```json
{
  "artifact_id": "art_20260530_abc123",
  "name": "report.pdf",
  "kind": "pdf",
  "size": 428912,
  "sha256": "...",
  "expires_at": "2026-05-31T16:00:00Z",
  "download_url": "https://...",
  "local_path": "/home/user/.hermes/artifacts/...",
  "delivery": ["native_attachment", "signed_url"]
}
```

The agent should call the publishing abstraction, not reason about S3/R2/MinIO/gateway internals.

## Delivery policy

- Code/repository outputs: GitHub branch/PR/release asset.
- Final user-facing artifacts (`.pdf`, `.docx`, `.xlsx`, `.pptx`, `.zip`, `.html`, `.csv`, images): artifact publisher.
- Mixed outputs: publish a ZIP via artifact publisher; use GitHub only for code.
- Small files: attempt native gateway attachment and include a signed URL fallback.
- Large files or unsupported gateways: signed URL only.
- Multiple artifacts: bundle into ZIP plus individual receipts when useful.

## Storage backend preference

Default to S3-compatible object storage:

1. Cloudflare R2 for remote gateway/user delivery.
2. MinIO for self-hosted/local/institutional deployments.
3. AWS S3 when the environment already uses AWS.

Signed URLs are the common durable pattern across commercial and community systems: S3 presigned URLs, E2B/OpenComputer sandbox download URLs, Composio-style file intermediaries, and AI API file IDs/download APIs.

## Local manifest

Every publication should create a local record under:

```text
~/.hermes/artifacts/{session_id}/{artifact_id}/
```

Include:
- original file or bundle;
- `manifest.json`;
- size, MIME, SHA-256;
- source session/job;
- delivery target/status;
- expiry/revocation metadata.

This supports audit, republish, cleanup, briefing, and future durable artifact libraries.

## Security baseline

- private bucket;
- short TTL by default;
- SHA-256 checksum;
- MIME sniffing, not extension-only trust;
- denylist credentials/system paths;
- path traversal protection;
- per-user/profile/session prefixes;
- logs must not expose full signed tokens;
- revocation by object deletion or token invalidation;
- never place storage credentials in prompts, memory, acervo, or user-visible output.

## Draft-First boundary

Publishing an ephemeral artifact back to the requesting user in the current channel can be part of the requested deliverable.

Publishing to third parties, shared drives, public links, durable collaboration spaces, or changing visibility beyond the current user/chat requires Draft-First approval.

## Implementation phases

1. Local convention: `~/.hermes/artifacts/`, manifest, checksums, MIME, gateway `MEDIA:` fallback.
2. S3-compatible backend: upload + signed URL + TTL.
3. Tool/MCP: `publish_artifact`, `publish_many`, `make_zip`, `revoke_artifact`, `list_recent_artifacts`, `create_signed_upload_url`, `create_signed_download_url`.
4. Gateway integration: use receipt to decide native attachment vs signed URL; preserve fallback.
