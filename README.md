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

| Problema                                                                      | Severidade | Arquivo                                    | Linha              | Observação                                                                             |
|:------------------------------------------------------------------------------|:-----------|:-------------------------------------------|:-------------------|:---------------------------------------------------------------------------------------|
| **Chaves expostas** no código                                                 | CRITICAL   | `app.py`/`controllers.py`                  | 7/289              | `app.config["SECRET_KEY"]` hard-coded / `secret_key` no endpoint de `health_check`     |
| Modo #sóvai, ou seja, **ausência de confirmação** para operações críticas     | HIGH       | `app.py`                                   | 48                 | Função `reset_database`                                                                |
| **Rotas sensíveis desprotegidas** sem middleware de autenticação              | HIGH       | `app.py`                                   | 47                 | Rota `/admin/reset-db`                                                                 |
| **Senhas descriptografadas**                                                  | MEDIUM     | `database.py`                              | 76                 | Poderia dar um desconto por ser um mock e talvez ter sido intencional, MAAAS...        |
| Não encontrei um `db_connection.close` para fechar conexão com banco de dados | MEDIUM     | `database.py`                              | *Não especificado* | Fechar conexão com o banco de dados para evitar leak de memória e performance          |
| **Excesso de responsabilidades** nos carecendo de separação (SRP) em serviços | LOW        | `controllers.py`/`database.py`/`models.py` | *Não especificado* | Aplicação de Service Layer Pattern                                                     |
| Modo **Debug** ativado                                                        | LOW        | `app.py`                                   | 8                  | Interessante ativar de acordo com o ambiente de execução                               |

### ecommerce-api-legacy

### task-manager-api

---