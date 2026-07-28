# Heurísticas de Análise de Projeto (Fase 1)

Este documento é agnóstico de tecnologia: descreve *como procurar* sinais, não uma lista fechada de stacks. Para adicionar suporte a um novo ecossistema, basta adicionar uma linha nas tabelas abaixo.

## 1. Arquivos de entrada para inspecionar primeiro

Sempre comece pelos arquivos-manifesto, na raiz do projeto-alvo:

| Ecossistema | Manifesto | Lockfile (versões exatas) |
|---|---|---|
| Python | `requirements.txt`, `Pipfile`, `pyproject.toml` | `Pipfile.lock`, `poetry.lock` |
| Node.js | `package.json` | `package-lock.json`, `yarn.lock` |
| Go | `go.mod` | `go.sum` |
| Java | `pom.xml`, `build.gradle` | — |
| Ruby | `Gemfile` | `Gemfile.lock` |

Também procure arquivos de configuração (`.env`, `.env.example`, `settings.py`, `config.js`, `config/*.yml`) — indicam variáveis de ambiente esperadas e, às vezes, segredos hardcoded (relevante para o catálogo de anti-patterns).

## 2. Detecção de linguagem

- Sinal primário: presença de um manifesto da tabela acima.
- Sinal secundário: censo de extensões de arquivo-fonte (`.py`, `.js`/`.ts`, `.go`, `.rb`, `.java`) — a extensão predominante entre os arquivos não excluídos (ver seção 8) é a linguagem do projeto.
- Fallback (sem manifesto): shebang da primeira linha (`#!/usr/bin/env python3`) ou sintaxe característica no arquivo de entrada.

## 3. Detecção de framework

Verifique o nome da dependência no manifesto **e** confirme com uma importação real no código (evita falso positivo de dependência transitiva/não usada):

| Framework | Sinal no manifesto | Sinal no código |
|---|---|---|
| Flask | `flask` | `from flask import Flask`, `app = Flask(__name__)` |
| Django | `django` | `manage.py` na raiz, `INSTALLED_APPS` em `settings.py` |
| FastAPI | `fastapi` | `from fastapi import FastAPI` |
| Express | `express` | `require('express')` / `import express from 'express'`, `app.listen(...)` |
| Koa | `koa` | `new Koa()` |
| NestJS | `@nestjs/core` | decorators `@Controller`, `@Module` |

Regra genérica para frameworks não listados: procure o nome de cada dependência direta do manifesto como substring de `import`/`require` no(s) arquivo(s) de entrada; o primeiro que instancia um objeto tipo "app"/"server" é o framework web.

**Extração de versão**: prefira o lockfile (versão resolvida exata); na ausência dele, use o especificador do manifesto (ex.: `Flask==3.1.1` → `3.1.1`; `"express": "^4.18.2"` → `4.18.2`).

## 4. Resumo de dependências a imprimir

Não liste todas as dependências — apenas as diretas e arquiteturalmente relevantes: framework web, driver/ORM de banco, biblioteca de auth, biblioteca de serialização/validação. Ignore dependências de dev/test (`pytest`, `nodemon`, etc.) no campo `Dependencies:` da Fase 1.

## 5. Detecção de banco de dados

Sinais, em ordem de confiabilidade:

1. Import de driver: `sqlite3`, `psycopg2`/`psycopg`, `pymongo`, `mysql.connector`/`mysql2`, `sqlite3` (Node built-in).
2. String de conexão ou variável de ambiente: `DATABASE_URL`, `MONGO_URI`, caminho de arquivo `.db`.
3. Classes de ORM: `class X(db.Model)` (SQLAlchemy), `mongoose.Schema(...)`, `sequelize.define(...)`.
4. **DDL inline** (`CREATE TABLE ...` embutido em uma função Python/JS) — comum em projetos legados sem migrations. Trate isso como sinal de banco de dados válido e também como candidato a anti-pattern (schema acoplado ao código, sem migrations).

**Nomes de tabela**: extraia sempre da DDL (`CREATE TABLE nome (...)`) ou dos nomes de classe de modelo/schema — nunca infira por adivinhação a partir do domínio.

## 6. Inferência de domínio

Combine nomes de rota (`/produtos`, `/pedidos`, `/tasks`) com nomes de tabela/modelo para produzir um rótulo curto + lista de entidades entre parênteses, no formato:

```
Domain:        E-commerce API (produtos, pedidos, usuários)
```

## 7. Classificação da arquitetura atual

Calcule dois sinais e combine-os — a presença de pastas por si só não basta:

1. **Separação por diretório**: existem `models/`, `views/`/`routes/`, `controllers/` (ou equivalentes) como diretórios distintos?
2. **Sinal de "God File"**: existe algum arquivo-fonte único acima de ~150-200 linhas que mistura roteamento HTTP + acesso a banco + lógica de negócio no mesmo arquivo? Isso é verdade mesmo quando diretórios "corretos" já existem (ex.: um `routes/task_routes.py` que também monta serialização e lógica de negócio manualmente é um God File dentro da pasta certa).

Classifique como:
- **Monolítica** — sem separação de diretórios, tudo em poucos arquivos flat. Justificativa: `"tudo em N arquivos, sem separação de camadas"`.
- **Parcialmente organizada** — diretórios existem, mas um ou mais deles contêm lógica que pertence a outra camada (God File dentro da pasta certa). Justificativa: nomeie qual camada está inchada e com o quê (ex.: `"routes/ atuam como controller+view+serializer"`).
- **MVC-alinhada** — diretórios existem e cada arquivo respeita a responsabilidade da sua camada (ver `mvc-guidelines.md`).

## 8. Contagem de arquivos-fonte analisados

Inclua apenas arquivos-fonte do próprio projeto. Exclua sempre:

- Diretórios de dependências instaladas: `node_modules/`, `venv/`, `.venv/`, `__pycache__/`, `vendor/`.
- Controle de versão: `.git/`.
- Lockfiles: `package-lock.json`, `poetry.lock`, etc.
- Diretórios de teste (`tests/`, `test/`, `*_test.py`, `*.test.js`) — a menos que a auditoria seja explicitamente sobre a suíte de testes.
- Artefatos gerados/build (`dist/`, `build/`, `*.pyc`).

O número reportado em `Source files: N files analyzed` deve refletir exatamente essa contagem — se alguém recontar manualmente, o número deve bater.

## 9. Extensibilidade

Estas heurísticas são baseadas em padrões (nome de dependência + assinatura de import/decorator), não em uma lista fechada. Para suportar um novo ecossistema, adicione uma linha nas tabelas das seções 1 e 3 — nenhuma outra parte da skill precisa mudar.
