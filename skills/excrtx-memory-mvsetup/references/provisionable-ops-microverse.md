# Provisionable ops microverse pattern

Use this reference when promoting an already-running Acervo microverse into the replicable Exocórtex setup.

## Case class

A runtime microverse already exists and has useful operational content. The user wants it made provisionable for future installs, but the setup script must not overwrite local evolution.

## Recommended sequence

1. Audit the runtime microverse first.
2. Capture a functional `before` snapshot under the microverse, not only in chat.
3. Enrich the microverse with reusable governance artifacts:
   - provision manifest;
   - drift register;
   - profile/MCP/cron/version registries;
   - Draft-First, secret-handling, runtime-verification and rollback contracts;
   - base-provisioning and post-change-validation workflows;
   - change-draft, healthcheck and runtime-snapshot templates.
4. Prepare the installer/setup change as DRAFT only.
5. Apply the setup patch only after explicit approval.

## Runtime seed vs source seed

Do not simply copy the runtime microverse into the installer source and rely on the setup's generic Acervo copy step.

If the setup uses a generic copy such as:

```bash
rsync -a "$ACERVO_SRC/" "$ACERVO/"
```

then adding a base microverse under source can overwrite local runtime evolution on future setup runs.

Use this pattern instead:

```bash
rsync -a \
  --exclude '__pycache__' \
  --exclude 'micro/{slug}/***' \
  "$ACERVO_SRC/" "$ACERVO/"

MICRO_SRC="$ACERVO_SRC/micro/{slug}"
MICRO_DST="$ACERVO/micro/{slug}"
mkdir -p "$MICRO_DST"
rsync -a --ignore-existing --exclude '__pycache__' "$MICRO_SRC/" "$MICRO_DST/"
```

If `rsync` is unavailable, avoid a destructive `cp -r` fallback for base microverses. Either implement a preserving fallback with `find` and `install -D` only when the target is absent, or skip with a warning.

## Idempotency tests

Run these before applying the final setup patch:

```bash
bash -n setup.sh

tmp_root="$(mktemp -d)"
HERMES_HOME="$tmp_root/hermes" EXOCORTEX_HOME="$tmp_root/exocortex" bash setup.sh

find "$tmp_root/exocortex/acervo/micro/{slug}" -type f -print0 \
  | sort -z | xargs -0 sha256sum > "$tmp_root/before.sha256"

HERMES_HOME="$tmp_root/hermes" EXOCORTEX_HOME="$tmp_root/exocortex" bash setup.sh

find "$tmp_root/exocortex/acervo/micro/{slug}" -type f -print0 \
  | sort -z | xargs -0 sha256sum > "$tmp_root/after.sha256"

diff -u "$tmp_root/before.sha256" "$tmp_root/after.sha256"
```

Also test local preservation:

```bash
echo LOCAL_MUTATION_TEST >> "$tmp_root/exocortex/acervo/micro/{slug}/knowledge/runtime-map.md"
sha256sum "$tmp_root/exocortex/acervo/micro/{slug}/knowledge/runtime-map.md" > "$tmp_root/local.before"
HERMES_HOME="$tmp_root/hermes" EXOCORTEX_HOME="$tmp_root/exocortex" bash setup.sh
sha256sum "$tmp_root/exocortex/acervo/micro/{slug}/knowledge/runtime-map.md" > "$tmp_root/local.after"
diff -u "$tmp_root/local.before" "$tmp_root/local.after"
grep -q LOCAL_MUTATION_TEST "$tmp_root/exocortex/acervo/micro/{slug}/knowledge/runtime-map.md"
```

Expected result: diffs are empty and the local mutation survives.

## Snapshot contents

A functional snapshot should include:

- timestamp and active profile;
- Hermes version;
- Acervo canonical realpath;
- profiles observed;
- MCPs observed;
- memory provider status;
- file list of the microverse;
- setup script syntax status;
- installer git status if applicable;
- known drift and severity;
- exact commands/tools used for evidence.

## Acervo v2 shape

Some older guidance mentions root `SCHEMA.md`, `index.md`, and `log.md`. For Acervo v2 microverses using `_meta/`, preserve the current shape:

```text
micro/{slug}/microverso.yaml
micro/{slug}/_meta/SCHEMA.md
micro/{slug}/_meta/index.md
micro/{slug}/_meta/log.md
```

Do not regress a v2 microverse to the older root-file layout just to match an older template.
