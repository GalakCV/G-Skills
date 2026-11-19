# G-Skills

Skills de segurança ofensiva no padrão **router + technique cards**, para rodar no
DeepSeek Harness (DSH) com subagentes. Cada skill tem um `SKILL.md` que roteia por fase,
cards de técnica compactos em `techniques/` (o agente abre só o card da fase atual, pra
manter o contexto enxuto), e um `safety.md` com os gates determinísticos.

## Skills

### `recon/` — reconhecimento web para bug bounty autorizado
Dado um escopo, mapeia a superfície de ataque de ponta a ponta e entrega um inventário
completo e anotado com sinais — **cobertura, não poda; o caçador decide**.

Fases: `passive-enum` → `active-discovery` → `http-probe` → `js-recon` →
`content-fuzzing` (intrusivo, precisa aprovação) → `surface-mapping`.

### `code-audit/` — auditoria de código-fonte para pesquisa de 0-day/CVE em OSS
Dado um repositório, mapeia a superfície, roda SAST (Semgrep + CodeQL quando disponível)
e tria os achados numa lista curta e honesta de vulnerabilidades confirmadas — **precisão
acima de recall; o motor acha, o agente julga**.

Fases: `sink-mapping` → `sast-scan` → `sast-triage` → `dataflow-trace` →
`patch-diff-hunt` (n-day → 0-day) → `reporting`.

## Instalação (DSH)

```bash
# global por usuário — toda sessão do DSH enxerga
cp -r recon code-audit ~/.agents/skills/
```

Recarregue a sessão do DSH e as skills `recon` e `code-audit` ficam disponíveis para os
agentes.

## Princípios

- **O agente decide, as ferramentas executam e protegem** — escopo, redação de segredo e
  rate-limit ficam determinísticos, no `safety.md`.
- **Confirmado vs hipótese** — nada é reportado como confirmado sem evidência observada.
- **Verdade determinística acima de achismo** — status HTTP, resolução DNS e caminhos de
  taint vêm de observação, não de suposição.
