# Drive-first export policy for Frontend Slides

## Default

`exocortex-frontend-slides` produces local final artifacts first and offers private Google Drive upload as the standard next step.

Ask the user whether they want the upload unless they already requested it explicitly. If they say yes, upload privately to the user's Drive using the Exocórtex path rules. This avoids asking a normal user to create or authenticate a Vercel account just to receive a deck.

## Export stack

- `deck.html` — browser presentation.
- `deck.pdf` — static distribution.
- `deck.zip` — complete package: source Markdown, HTML, PDF, assets, manifest.
- `receipt.google_drive.json` — proof of private publication.

## Drive path rules

Never upload final deck artifacts to the Drive root.

Fallback when context is missing:

```text
exocortex/inbox
```

Preferred presentation destinations:

```text
exocortex/{microverso}/{ano}/apresentacoes
exocortex/ensino/{ano}/{disciplina}/slides-premium
exocortex/gabinete/{ano}/apresentacoes
exocortex/dev/{ano}/apresentacoes
exocortex/estudio-criativo/{ano}/decks
```

Resolve or create each folder segment before uploading. Record `folder_path`, `folder_id`, file IDs and links in the artifact receipt.

## When to use Vercel

Use Vercel only when all conditions hold:

1. User explicitly wants a public URL.
2. User approves the Draft-First summary.
3. User accepts external account/tooling friction.
4. The artifact does not contain sensitive/private content.

## Rule

Do not mention Vercel as the natural next step after deck generation. The natural next step is Drive export or local ZIP/PDF delivery.
