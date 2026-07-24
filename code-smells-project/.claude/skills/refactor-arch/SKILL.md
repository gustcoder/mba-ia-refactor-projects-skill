---
name: refactor-arch
description: Analisa uma codebase (qualquer linguagem/framework), detecta arquitetura e anti-patterns, gera um relatório de auditoria com severidade/arquivo/linha, e refatora para MVC após confirmação, validando que a aplicação continua funcionando. Use quando o usuário pedir para auditar arquitetura, revisar code smells, ou refatorar um projeto legado para MVC.
disable-model-invocation: true # evita disparo automático da skill durante outras tarefas; só executa via /refactor-arch explícito
---

# refactor-arch

Skill de 3 fases sequenciais para analisar, auditar e refatorar um projeto para o padrão MVC (Model-View-Controller), **agnóstica de linguagem e framework**.

Opera sobre o projeto onde está instalada (diretório de trabalho atual = raiz do projeto-alvo). Nunca trate o repositório onde este arquivo `SKILL.md` fisicamente reside como algo diferente do projeto-alvo — a skill é copiada dentro de cada projeto e roda a partir de lá.

## Resolução de paths (cross-cutting, vale para todas as fases)

**Raiz do repositório de desafio** (onde fica `reports/`): a partir do diretório de trabalho atual, suba diretórios procurando uma pasta chamada `reports/` que seja irmã do diretório do projeto-alvo (ex.: se o projeto-alvo é `code-smells-project/`, a raiz é o pai desse diretório, e deve conter `reports/`). Se não encontrar em até 3 níveis acima, use `./reports/` relativo ao diretório de trabalho atual como fallback e avise o usuário no output que o fallback foi usado.

**Nome do arquivo de relatório**: liste `reports/audit-project-*.md` já existentes na raiz encontrada acima. Use o próximo número inteiro livre (`N`); se nenhum existir, `N=1`. Não sobrescreva relatórios existentes de outros projetos.

## Fase 1 — Análise (Project Analysis)

1. Leia `references/project-analysis.md` e aplique as heurísticas de detecção nele descritas.
2. Detecte: linguagem, framework + versão, dependências relevantes, tecnologia de banco de dados, domínio do projeto (inferido de rotas/tabelas), e a arquitetura atual (monolítica / parcialmente organizada / MVC-alinhada).
3. Enumere os arquivos-fonte analisados, aplicando as exclusões descritas em `project-analysis.md` (dependências instaladas, VCS, lockfiles, testes).
4. Não modifique nenhum arquivo nesta fase.
5. Imprima exatamente este formato (preserve os rótulos e o espaçamento tal como abaixo, incluindo o espaçamento irregular em "Framework:"):

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      <linguagem>
Framework:      <framework e versão>
Dependencies:  <dependências relevantes>
Domain:        <domínio> (<entidades principais>)
Architecture:  <classificação> — <justificativa curta>
Source files:  <N> files analyzed
DB tables:     <tabelas/coleções>
================================
```

## Fase 2 — Auditoria (Audit)

1. Leia `references/anti-pattern-catalog.md`.
2. Para cada anti-pattern do catálogo, cruze os sinais de detecção contra o código real — **leia** cada arquivo listado na Fase 1, não apenas espie trechos. Cite `arquivo:linha` (ou intervalo de linhas) sempre a partir da leitura real, nunca estimado.
3. Para cada ocorrência encontrada, monte um finding com severidade, arquivo/linha, descrição, impacto e recomendação, seguindo exatamente `references/report-template.md`.
4. Calcule a contagem por severidade (sempre liste as 4, mesmo com contagem 0) e o total de findings.
5. Salve o relatório completo em `<raiz-do-repo>/reports/audit-project-<N>.md` (conteúdo do relatório apenas — sem a linha de prompt `[y/n]`, que é só interativa).
6. Imprima o mesmo relatório no stdout, seguido da linha de prompt.

**Gate obrigatório — leia com atenção:** depois de imprimir o relatório, você DEVE parar e perguntar literalmente:

```
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

Não prossiga para a Fase 3 — nem leia arquivos com a intenção de refatorá-los — sem uma confirmação explícita e afirmativa (`y`/"sim"/equivalente) do usuário. Se a resposta for negativa, pare completamente e não toque em nenhum arquivo. Esta é a regra de segurança mais importante desta skill; não a contorne mesmo que o usuário peça pressa.

## Fase 3 — Refatoração (Refactoring)

Só execute esta fase após confirmação explícita na Fase 2.

1. Leia `references/mvc-guidelines.md` (arquitetura-alvo) e `references/refactoring-playbook.md` (transformações concretas).
2. Aplique as transformações do playbook correspondentes a cada finding do relatório da Fase 2, na ordem CRITICAL → HIGH → MEDIUM → LOW.
3. Se o projeto já tiver diretórios parcialmente alinhados ao MVC (ex.: `models/`, `routes/`, `services/` já existentes e razoáveis), **não reconstrua do zero** — apenas mova/corrija o que viola a separação de camadas. Reconstrua a estrutura completa apenas quando o projeto for de fato um monólito sem separação.
4. Preserve os contratos de API externos (rotas, formatos de resposta) sempre que possível. Quando uma correção de segurança exigir mudança de comportamento (ex.: remover um endpoint administrativo desprotegido), aplique a mudança mas reporte-a explicitamente no output — nunca faça isso silenciosamente.
5. **Validação** (obrigatória, não pule nem finja resultado):
   - Detecte o comando de boot a partir do manifest do projeto (mesma heurística de `project-analysis.md`).
   - Suba a aplicação em background, aguarde e verifique ausência de erro/traceback no log de inicialização.
   - Para cada rota distinta identificada nas Fases 1/2, faça uma requisição e confirme resposta não-5xx (uma rota agora protegida por auth respondendo 401/403 é aceitável e deve ser anotada como tal).
   - Encerre o processo da aplicação ao final.
   - Se qualquer verificação falhar, **não marque como sucesso** — corrija e revalide, ou pare e reporte a falha honestamente.
6. Imprima exatamente este formato ao final:

```
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
<árvore de diretórios resultante>

## Validation
  <✓ ou ✗> Application boots without errors
  <✓ ou ✗> All endpoints respond correctly
  <✓ ou ✗> Zero anti-patterns remaining
================================
```

## Arquivos de referência

- `references/project-analysis.md` — Fase 1: heurísticas de detecção de linguagem, framework, banco de dados e arquitetura.
- `references/anti-pattern-catalog.md` — Fase 2: catálogo de anti-patterns, sinais de detecção e severidades.
- `references/report-template.md` — Fase 2: estrutura exata do relatório de auditoria.
- `references/mvc-guidelines.md` — Fase 3: regras da arquitetura MVC alvo.
- `references/refactoring-playbook.md` — Fase 3: padrões de transformação antes/depois.
