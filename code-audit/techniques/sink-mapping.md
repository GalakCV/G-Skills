# Technique: sink mapping (phase 1)

Goal: before scanning, tell the audit where risk concentrates for THIS repo's stack, so
Semgrep/CodeQL and dataflow focus on real attack surface instead of generic noise.

You reason from the languages, frameworks, and a sample of files — you do NOT read the
whole repo here.

## Produce

- **Entrypoints** (where untrusted input enters): HTTP routes/controllers, CLI args,
  message consumers, webhooks, file/upload handlers, deserialization entry, template
  rendering.
- **Sinks by class** — name the concrete functions/APIs for this stack:
  - Command injection: `os.system`, `subprocess(shell=True)`, `exec`, `child_process.exec`
  - SQLi: raw query concat, f-string/format SQL, ORM `.raw()`
  - Path traversal: `open`, `fs.readFile`, `sendFile`, `os.path.join` with input
  - SSRF: outbound `requests`/`fetch`/`http` with user-controlled URL
  - Deserialization: `pickle`, `yaml.load`, `Marshal`, `ObjectInputStream`, `unserialize`
  - Template/SSTI, XSS sinks, open redirect, XXE, code eval
- **Sources**: request params/body/headers, cookies, env, file contents, DB reads.
- **Framework/custom sinks** a stock ruleset won't know: the project's own
  `db.raw_query`, `render_unsafe`, `utils.shell.run`, etc.

## Output (JSON, reasoning_trace first)

```
{"reasoning_trace": "...",
 "entrypoints": ["flask routes in app/views.py"],
 "sinks": [{"class":"sqli","apis":["cursor.execute with f-string"]}],
 "sources": ["request.args","request.json","request.files"],
 "custom_sinks": ["core.db.raw_query","utils.shell.run"]}
```

Keep lists focused on what actually appears in this stack. This map seeds the scan's
rule selection.
