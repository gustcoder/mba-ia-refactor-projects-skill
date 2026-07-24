# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
pip install -r requirements.txt
export SECRET_KEY="alguma-chave-secreta-so-sua"  # obrigatório, sem default (ver .env.example)
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado automaticamente no primeiro boot, já com produtos e usuários de exemplo (senhas seed já são armazenadas com hash).

## Arquitetura

```
config/       # configuração via variável de ambiente (SECRET_KEY, DEBUG, DATABASE_PATH)
models/       # acesso a dados e regras de negócio por entidade (produto, usuario, pedido)
controllers/  # orquestração: recebe input da rota, chama o Model, monta a resposta
routes/       # camada HTTP: registro de rotas, tradução HTTP <-> controller
middlewares/  # autenticação (JWT) e tratamento centralizado de erro
database.py   # fábrica de conexão SQLite (usada uma única vez pelo composition root)
app.py        # composition root: monta config + conexão + models + controllers + rotas
```

## Autenticação

`POST /login` retorna um JWT (`token`) válido por 8h. Rotas administrativas (`/admin/reset-db`) exigem esse token no header `Authorization: Bearer <token>` de um usuário com `tipo = "admin"` (o usuário seed `admin@loja.com` / `admin123` já tem esse papel).
