# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.

## Como rodar

```bash
npm install
cp .env.example .env   # preencha ADMIN_API_KEY e PAYMENT_GATEWAY_KEY
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

Exemplos de requisições estão em `api.http`.

## Autenticação de rotas administrativas

`GET /api/admin/financial-report` e `DELETE /api/users/:id` agora exigem o header `x-admin-key` com o valor de `ADMIN_API_KEY` — antes eram acessíveis sem nenhuma autenticação (ver relatório de auditoria).
