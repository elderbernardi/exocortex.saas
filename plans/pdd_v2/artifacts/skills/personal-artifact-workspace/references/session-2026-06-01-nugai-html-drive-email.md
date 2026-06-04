# Session reference: HTML artifact → Drive upload → Gmail draft

Context: user asked for a responsive HTML protocol for a NUGAI event, then asked to upload it to Drive and send the Drive link by email.

Durable pattern captured:

1. Treat the local HTML/ZIP as a final human-consumption artifact.
2. Preserve source Markdown and final exports in `~/.hermes/acervo/_artifacts/{artifact_id}/`.
3. Upload final exports privately to Drive under the Exocortex hierarchy, not the Drive root.
   - Preferred path for institutional teaching/event artifacts: `exocortex/ensino/{year}/palestras` when the event lives under the palestra harness.
   - Create missing intermediate folders explicitly and record the final `folder_id`.
4. Register a `receipt.google_drive.json` with folder link, file IDs, file links, MIME, SHA-256 and sizes.
5. If the user also asks to email the link, stop at DRAFT after Drive upload.
   - Uploading privately to the user's own Drive is execution of the requested delivery artifact.
   - Sending email is external communication and still requires explicit approval.
6. Draft body should include the HTML link, ZIP link and folder link when available.

Useful wording for the draft:

```text
Para: {recipient}
Assunto: Protocolo do evento NUGAI — Semana do Meio Ambiente

Segue o link para o protocolo do evento do NUGAI, em versão HTML responsiva, junto com o pacote ZIP contendo o HTML e a fonte Markdown.

HTML:
{html_link}

ZIP:
{zip_link}

Pasta no Drive:
{folder_link}
```

Pitfall: do not interpret "suba no Drive e envie o link" as approval to send the email. The upload and the email are different action classes. Execute the private upload; present the email as DRAFT and wait for "enviar" or equivalent.
