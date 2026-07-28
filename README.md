# 🚀 Desafio MBA Engenharia de Software com IA - Full Cycle

![Status](https://img.shields.io/badge/Status-Em%20Progresso-orange?style=for-the-badge&logo=github)
![IA](https://img.shields.io/badge/Focus-AI%20Engineering-blueviolet?style=for-the-badge&logo=openai)
![FullCycle](https://img.shields.io/badge/School-FullCycle-yellow?style=for-the-badge)

## Objetivo

Entregar uma Skill capaz de:

- Analisar uma codebase detectando linguagem, framework e arquitetura atual
- Identificar anti-patterns e code smells, classificando por severidade com arquivo e linha exatos
- Gerar um relatório de auditoria estruturado com todos os achados
- Refatorar o projeto para o padrão MVC (Model-View-Controller), eliminando os problemas encontrados
- Validar o resultado garantindo que a aplicação continua funcionando após as mudanças

A skill deve ser agnóstica de tecnologia, funcionando com diferentes linguagens e frameworks.

---

## 🛠️ Tecnologias e Requisitos

* **Ferramenta Escolhida**: Claude Code
* **Recurso:** Custom Skills (ou o equivalente na ferramenta escolhida)
* **Formato dos arquivos de referência:** Markdown
* **Projetos-alvo:** Python/Flask (2 projetos) e Node.js/Express (1 projeto) (fornecidos no repositório base)

## ️🕵️ Análise Manual

Esta sessão consiste em elencar os problemas que encontrei por análise manual realizada antes de construir as skills.

### code-smells-project

| Problema                                                                      | Severidade | Arquivo                   | Linha | Justificativa                                                                      |
|:------------------------------------------------------------------------------|:-----------|:--------------------------|:------|:-----------------------------------------------------------------------------------|
| **Chaves expostas** no código                                                 | CRITICAL   | `app.py`/`controllers.py` | 7/289 | `app.config["SECRET_KEY"]` hard-coded / `secret_key` no endpoint de `health_check` |
| **Excesso de responsabilidades** carecendo de separação (SRP) em contextos    | CRITICAL   | `controllers.py`          | 24    | Necessária a aplicação de Service Layer Pattern                                    |
| Modo #sóvai, ou seja, **ausência de confirmação** para operações críticas     | HIGH       | `app.py`                  | 48    | Função `reset_database`                                                            |
| **Rotas sensíveis desprotegidas** sem middleware de autenticação              | HIGH       | `app.py`                  | 47    | Rota `/admin/reset-db`                                                             |
| **Senhas descriptografadas**                                                  | MEDIUM     | `database.py`             | 76    | Poderia dar um desconto por ser um mock e talvez ter sido intencional, MAAAS...    |
| Não encontrei um `db_connection.close` para fechar conexão com banco de dados | MEDIUM     | `database.py`             | 10    | Fechar conexão com o banco de dados para evitar leak de memória e performance      |
| Nenhuma versão de API no path (/produtos em vez de /v1/produtos)              | LOW        | `app.py`                  | 11    | Dificulta evolução futura sem quebrar clientes                                     |
| Modo **Debug** ativado                                                        | LOW        | `app.py`                  | 8     | Interessante ativar de acordo com o ambiente de execução                           |

### ecommerce-api-legacy

| Problema                                          | Severidade | Arquivo                                          | Linha  | Justificativa                                                                                                        |
|:--------------------------------------------------|:-----------|:-------------------------------------------------|:-------|:---------------------------------------------------------------------------------------------------------------------|
| **Chaves expostas** no código                     | CRITICAL   | `src/utils.js`                                   | 3/4    | `dbPass` e `paymentGatewayKey` hard-coded #maldade                                                                   |
| **GodClass** concentrando toda a carga estrutural | CRITICAL   | `src/AppManager.js`                              | 1-141  | Necessário aplicar os conceitos de MVC para separação de responsabilidades                                           |
| Criptografia fraca                                | HIGH       | `src/utils.js`                                   | 17-23  | Base64 pode facilmente ser revertido e gerar problema de seguranaça                                                  |
| Código-Macarrão                                   | MEDIUM     | `src/AppManager.js`                              | 28-78  | Vários níveis de identação misturando muita coisa. Interessante externalizar funções e aplicar o Object-Calisthenics |
| Complexidade n+1                                  | MEDIUM     | `src/AppManager.js`                              | 89-127 | Utilizar `JOIN` entre as tabelas para evitar `foreach` desnecessários                                                |
| Quebras de linha sem padrão após `if`             | LOW        | `src/AppManager.js`                              | 67     | Falta de padrão no código afeta a legibilidade do mesmo                                                              |
| Nomes de variável pouco descritivos               | LOW        | `src/AppManager.js`                              | 29-33  | "O óbvio tem que ser dito"                                                                                           |

### task-manager-api

---

## ️🚧️ Construção da Skill

### Q1. Decisões de design: como estruturou o SKILL.md e os arquivos de referência**
R.: Utilizei as técnicas de **SDD** para estruturar meu SKILL.md usando como apoio as próprias instruções do desafio.
Com isso elaborei e adaptei uma Spec para conter todos os requisitos necessários para alcançar o objetivo.
Utilizei a ideia do framework **Context Mesh**, por isso o projeto contém um diretório `.context/intent` onde armazenei minha spec.

### Q2. Quais anti-patterns incluiu no catálogo e por quê?
R.: 

| Anti-Pattern          | Severidade |
|-----------------------|------------|
| Hardcoded Credentials | CRITICAL   |
| God Class             | CRITICAL   |
| Confused Deputy       | HIGH       |
| Spaghetti Code        | MEDIUM     |
| Lava Flow             | LOW        |

Foram os anti-patterns mais gritantes e que me chamaram a atenção logo a primeira vista, por isso decidi registra-los como referência base para a skill.

### Q3. Como garantiu que a skill é agnóstica de tecnologia
R.: Criei uma sessão **Requisitos** na Spec onde cito os diretórios de exemplo e especifico que é expressamente obrigatório que seja agnóstica.

### Q4. Desafios encontrados e como resolveu
R.: Compor a spec inicial foi o primeiro desafio, pois consolidar uma ideia em um prompt eficiente é uma tarefa cirúgica.

## ️🏆 Resultados
- Resumo dos relatórios de auditoria dos 3 projetos (quantos findings por severidade em cada)
```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 8 | HIGH: 3 | MEDIUM: 4 | LOW: 3

================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express 4.22.1
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 3 | HIGH: 4 | MEDIUM: 4 | LOW: 2
```
- Comparação antes/depois da estrutura de cada projeto

**code-smells-project**

**Antes:**

<img width="388" height="430" alt="code-smells-project-before" src="https://github.com/user-attachments/assets/88793e34-24df-42ac-b08e-39bb134d152c" />

**Depois:**

<img width="388" height="823" alt="code-smells-project-after" src="https://github.com/user-attachments/assets/533b2812-bb76-479a-bad3-a095ea132f14" />

## Checklist de Validação :: code-smells-project

### Fase 1 — Análise
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask)
- [x] Domínio da aplicação descrito corretamente
- [x] Número de arquivos analisados condiz com a realidade (sim, 4)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados
- [ ] Detecção de APIs deprecated incluída (se aplicável)
- [x] Skill pausa e pede confirmação antes da Fase 3

<img width="657" height="496" alt="code-smells-project-phase3-confirmation" src="https://github.com/user-attachments/assets/ad6ee876-0934-41e0-b59d-193c2a3cdc87" />


### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded) (`config/settings`)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para visualização ou roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado (`middlewares/error_handler.py`)
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

---

## Checklist de Validação :: ecommerce-api-legacy

### Fase 1 — Análise
- [x] Linguagem detectada corretamente (Javascript/Node.js)
- [x] Framework detectado corretamente (Express 4.22.1)
- [x] Domínio da aplicação descrito corretamente
- [x] Número de arquivos analisados condiz com a realidade (sim, 4)

### Fase 2 — Auditoria
- [x] Relatório segue o template definido nos arquivos de referência
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados
- [x] Detecção de APIs deprecated incluída (src/AppManager.js:37-136)
- [x] Skill pausa e pede confirmação antes da Fase 3

<img width="657" height="496" alt="code-smells-project-phase3-confirmation" src="https://github.com/user-attachments/assets/ad6ee876-0934-41e0-b59d-193c2a3cdc87" />


### Fase 3 — Refatoração
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config (sem hardcoded) (`config/settings`)
- [x] Models criados para abstrair dados
- [x] Views/Routes separadas para visualização ou roteamento
- [x] Controllers concentram o fluxo da aplicação
- [x] Error handling centralizado (`middlewares/error_handler.py`)
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

- Screenshots ou logs mostrando as aplicações rodando após refatoração

**code-smells-project**

<img width="1892" height="802" alt="code-smells-project-phase3-final-log" src="https://github.com/user-attachments/assets/564f6c17-36b8-449e-a5b0-378aa4fec495" />

- Observações sobre como a skill se comportou em stacks diferentes

## ️💻 Como executar
- Ter o Claude Code CLI instalado e configurado
- A partir da raiz deste repositório, abrir o terminal, navegar até o diretório do projeto a ser analisado e executar o comando conforme exemplo abaixo:
```bash
cd code-smells-project
claude "/refactor-arch"
```
