# Objetivo

Criar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças
- A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

## Contexto
### Definição de Severidades

Para padronizar a auditoria e os relatórios gerados pela skill, utilize a seguinte escala de classificação baseada em problemas de MVC e SOLID:

- CRITICAL: Falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (ex: "God Class" contendo banco de dados, lógicas complexas e roteamento no mesmo arquivo).
- HIGH: Fortes violações do padrão MVC ou princípios SOLID que dificultam muito a manutenção e testes (ex: lógicas de negócio pesadas presas dentro de Controllers, forte acoplamento sem Injeção de Dependência, ou uso de estado global mutável em toda a aplicação).
- MEDIUM: Problemas de padronização, duplicação de código ou gargalos de performance moderada (ex: Queries N+1 no banco de dados, uso inadequado de middlewares, validações ausentes nas rotas).
- LOW: Melhorias de legibilidade, nomenclatura de variáveis ruins, ou "magic numbers" soltos pelo código.

## Estrutura para Criação de Skill

A skill deverá ser um arquivo `SKILL.md` contido em `.claude/skills/refactor-arch`.

Deve ser uma skill que os detecte, gere um relatório de auditoria e corrija automaticamente.

### Tarefas

Criar a skill dentro do projeto `.claude/skills/refactor-arch` e implementar o SKILL.md com 3 fases sequenciais:

- **Fase 1 — Análise:** Detectar stack, mapear arquitetura atual, imprimir resumo
- **Fase 2 — Auditoria:** Cruzar código contra catálogo de anti-patterns, gerar relatório, pedir confirmação
- **Fase 3 — Refatoração:** Reestruturar para o padrão MVC, validar que funciona

Crie também arquivos de referência em Markdown que forneçam à skill o conhecimento necessário para executar as 3 fases. 
Os arquivos devem cobrir **obrigatoriamente** as seguintes áreas de conhecimento:

| Área de conhecimento      | O que deve conter                                                                                     |
|---------------------------|-------------------------------------------------------------------------------------------------------|
| Análise de projeto        | Heurísticas para detecção de linguagem, framework, banco de dados e mapeamento de arquitetura         |
| Catálogo de anti-patterns | Anti-patterns com sinais de detecção e classificação de severidade                                    |
| Template de relatório     | Formato padronizado do relatório de auditoria (Fase 2)                                                |
| Guidelines de arquitetura | Regras do padrão MVC alvo (camadas Models, Views/Routes e Controllers, responsabilidades de cada uma) |
| Playbook de refatoração   | Padrões concretos de transformação para cada anti-pattern (com exemplos de código)                    |

> **Nota:** Você tem liberdade para organizar os arquivos de referência — vamos usar 1 arquivo para cada área de conhecimento.

## Catálogo de Anti-Patterns

Como exemplos de anti-patterns, vamos utilizar a seguinte classificação como referência:

| Anti-Pattern          | Severidade |
|-----------------------|------------|
| Hardcoded Credentials | CRITICAL   |
| God Class             | CRITICAL   |
| Confused Deputy       | HIGH       |
| Spaghetti Code        | MEDIUM     |
| Lava Flow             | LOW        |

## Requisitos da skill

- Deve ser agnóstica de tecnologia — deve funcionar corretamente nos 3 projetos fornecidos (`code-smells-project`, `ecommerce-api-legacy` e `task-manager-api`), independente da stack ou nível de organização
- O catálogo de anti-patterns deve conter no mínimo 8 anti-patterns com severidade distribuída (CRITICAL, HIGH, MEDIUM, LOW)
- O catálogo deve incluir detecção de APIs deprecated — identificar uso de APIs obsoletas e recomendar o equivalente moderno
- O playbook deve ter no mínimo 8 padrões de transformação com exemplos de código antes/depois
- A Fase 2 deve pausar e pedir confirmação antes de modificar qualquer arquivo
- A Fase 2 precisa gerar como output um relatório em `reports/`
- A Fase 3 deve validar o resultado (boot da aplicação + endpoints funcionando)

## Restrições
- Todas as 5 áreas de conhecimento precisam ser cobertas. 
- Os arquivos de referência devem serguir o padrão Markdown e precisam estar também dentro de `.claude/skills/refactor-arch`.
- O nome da skill (`refactor-arch`) e o arquivo `SKILL.md` são obrigatórios e não devem ser alterados.
- O path da skill segue a convenção da ferramenta escolhida (no Claude Code, por exemplo, é `.claude/skills/refactor-arch/`).

## Documento de Apoio

`README.md` -> Sessão "Análise Manual"

### Exemplo de Uso no CLI

```bash
# Executar a skill no projeto com problemas
cd code-smells-project
claude "/refactor-arch"
```

```
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python
Framework:      Flask 3.1.1
Dependencies:  flask-cors
Domain:        E-commerce API (produtos, pedidos, usuários)
Architecture:  Monolítica — tudo em 4 arquivos, sem separação de camadas
Source files:  4 files analyzed
DB tables:     produtos, usuarios, pedidos, itens_pedido
================================
```

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-350
Description: Arquivo único contém toda lógica de negócio, queries SQL, validação e formatação para 4 domínios diferentes.
Impact: Impossível testar em isolamento, qualquer mudança afeta tudo.
Recommendation: Separar em models e controllers por domínio.

### [CRITICAL] Hardcoded Credentials
File: app.py:8
Description: SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'
...

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
> y
```

```
[... refatoração executada ...]

================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
src/
├── config/settings.py
├── models/
│   ├── produto_model.py
│   └── usuario_model.py
├── views/
│   └── routes.py
├── controllers/
│   ├── produto_controller.py
│   └── pedido_controller.py
├── middlewares/error_handler.py
└── app.py (composition root)

## Validation
  ✓ Application boots without errors
  ✓ All endpoints respond correctly
  ✓ Zero anti-patterns remaining
================================
```
