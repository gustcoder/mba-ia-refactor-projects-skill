# Guidelines de Arquitetura MVC (Fase 3)

Regras da arquitetura-alvo, escritas de forma agnóstica de framework. Aplicam-se a Flask, Express, Django, FastAPI ou qualquer outro framework web.

## Responsabilidade de cada camada

### Models
- Dono da forma dos dados e do acesso à persistência (queries/ORM).
- Regras de negócio/invariantes que pertencem à própria entidade (ex.: `Task.is_overdue()`, validação de formato de e-mail).
- **Não** deve conhecer HTTP: sem `request`/`response`, sem status codes, sem rotas.

### Views / Routes
- Camada HTTP: registro de rotas, parsing de request (path params, query params, body), serialização da resposta e status code.
- Delega toda lógica para um Controller — a rota não decide regra de negócio, só traduz HTTP ⇄ chamada de controller.
- **Não** acessa banco de dados diretamente, **não** contém regra de negócio, **não** monta dict de resposta manualmente reimplementando lógica que já existe no Model (isso é duplicação — ver anti-pattern Spaghetti Code).

### Controllers
- Orquestra: recebe input já parseado da rota, chama métodos de Model/Service, monta o payload de resposta, traduz erros de domínio em respostas apropriadas.
- **Não** executa SQL cru, **não** manipula o objeto de request/response do framework além do que a rota já passou para ele.

## Onde entram as preocupações transversais

- **`config/`** — configuração vinda de variáveis de ambiente (segredos nunca hardcoded), um único ponto de composição por ambiente (dev/test/prod).
- **`middlewares/`** — autenticação/autorização, tratamento centralizado de erro, logging de requisição, validação de entrada — tudo que deve rodar de forma uniforme antes/ao redor dos handlers de rota.
- **Composition root** (`app.py`/`app.js`/equivalente) — único lugar responsável por instanciar e conectar config + conexão de banco + rotas + middlewares. Nenhuma outra parte do sistema deve se auto-instanciar dependências (isso é o anti-pattern de Tight Coupling/ausência de DI) — tudo é recebido de fora.

## Esqueleto de diretórios sugerido (genérico)

```
src/
├── config/
│   └── settings.{py,js}
├── models/
│   └── <entidade>.{py,js}
├── views/            (ou routes/, conforme convenção do ecossistema)
│   └── <entidade>_routes.{py,js}
├── controllers/
│   └── <entidade>_controller.{py,js}
├── middlewares/
│   └── error_handler.{py,js}
└── app.{py,js}        (composition root)
```

Mapeamento por ecossistema:
- **Flask**: `views/routes.py` com Blueprints (opcional), `models/*.py` como classes SQLAlchemy ou funções de acesso a dados puras.
- **Express**: `routes/*.js` com `express.Router()`, `models/*.js` como classes/funções de acesso a dados, `controllers/*.js` com funções exportadas chamadas pelas rotas.

## Regra de adaptação para projetos parcialmente organizados

Se o projeto já tem diretórios (`models/`, `routes/`, `services/`) que aproximadamente correspondem a este esqueleto, **não renomeie nem mova diretórios inteiros**. Em vez disso:
- Identifique qual arquivo dentro da pasta certa contém lógica da camada errada (ex.: um `routes/task_routes.py` que monta dicionários de resposta manualmente duplicando lógica que já existe em `models/task.py` — mover essa lógica para o model ou para um controller, não redesenhar a árvore de pastas).
- Só construa a estrutura completa do zero (esqueleto acima) quando o projeto for de fato um monólito flat, sem nenhuma separação prévia.

## Camada de Service (opcional)

É aceitável manter uma camada `services/` entre Controllers e Models para lógica de negócio reutilizável entre múltiplos controllers (ex.: envio de notificação, cálculo de relatório). Não remova uma camada de service já existente só porque o esqueleto canônico acima não a mostra — o problema real a corrigir é quando Controllers/Routes duplicam essa lógica em vez de reutilizar o Service.

## Ligação com SOLID

- **SRP** (Single Responsibility): cada Model cuida de uma entidade; cada Controller orquestra um conjunto coeso de casos de uso; cada Route só traduz HTTP. Um arquivo violando isso é o sinal do anti-pattern God Class.
- **DIP** (Dependency Inversion): dependências (conexão de banco, serviços externos) são recebidas via injeção no composition root, não instanciadas internamente pela classe que as usa — ausência disso é o anti-pattern Tight Coupling/No DI.

Use estas referências (SRP/DIP) diretamente no campo `Recommendation:` dos findings de Fase 2 relacionados a God Class, Confused Deputy e Tight Coupling.
