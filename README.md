# G-Skills

Skills de segurança ofensiva para **bug bounty autorizado**, no padrão **router + skill.yaml
+ scripts + runbooks + payloads** — skills auto-executáveis para o harness de bounty (e para
o DeepSeek Harness).

Cada skill tem:
- `SKILL.md` — router: metodologia + cards de fase
- `skill.yaml` — workflow executável (fases, tiers, scripts, dependências, I/O)
- `safety.md` — gates determinísticos (escopo, redação, não-destrutivo)
- `scripts/` — implementações reais (invocam as ferramentas)
- `runbooks/` — triagem e verificação manual
- `payloads/` — wordlists, fingerprints, markers de confirmação

## Skills

### Superfície de bounty (web / api / cloud / infra)

| Skill | Tier | O que faz |
|---|---|---|
| `recon` | passivo + ativo-seguro | mapeia a superfície e entrega o inventário anotado — cobertura, não poda |
| `web-testing` | intrusivo (gated) | access control (IDOR/BOLA), injection, SSRF, XSS (com reality check de CSP), file-upload, business-logic |
| `api-testing` | intrusivo (gated) | mineração de spec, auth enforcement (no-token), BOLA, BFLA, mass-assignment |
| `cloud` | intrusivo (gated) | buckets expostos, fingerprint de provider, alcance de metadata — só detecção, nunca rouba credencial |
| `infra` | intrusivo (gated) | subdomain takeover (dangling CNAME), painéis/serviços expostos, TLS, DNS — só prova, nunca reivindica |

### Auditoria de código (projeto separado)

| Skill | O que faz |
|---|---|
| `code-audit` | auditoria de código-fonte / 0-day em OSS (Semgrep/CodeQL) — usada pelo harness de code-audit, não pelo de bounty |

## Instalação

```bash
# global por usuário — toda sessão enxerga
cp -r recon web-testing api-testing cloud infra ~/.agents/skills/
# code-audit só se for usar o harness de auditoria de código
cp -r code-audit ~/.agents/skills/
```

## Princípios

- **O agente decide, as ferramentas executam e protegem** — escopo, redação de segredo e
  rate-limit ficam determinísticos, no `safety.md` + nos scripts.
- **Cobertura, não poda** — no recon, sinais anotam; nunca descartam superfície.
- **Detecção, não exploração** — cloud e infra provam alcance/exposição; não roubam
  credencial nem reivindicam recurso.
- **Confirmado vs hipótese** — nada é reportado como confirmado sem evidência observada.
- **Mínima evidência** — um request prova a maioria dos bugs; nunca dumpar dataset.

## Aviso

Use **apenas** contra alvos que você está autorizado a testar. As fases intrusivas
(web/api/cloud/infra) exigem autorização humana explícita e rodam só via o comando gated do
harness. Nenhuma skill executa exploit destrutivo.
