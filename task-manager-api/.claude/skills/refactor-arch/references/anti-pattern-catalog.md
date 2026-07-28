# Catálogo de Anti-Patterns (Fase 2)

## Como usar este catálogo

Para cada entrada abaixo, procure os sinais de detecção no código real do projeto-alvo (leitura completa dos arquivos, não apenas grep superficial). Cada ocorrência confirmada vira um finding no relatório de auditoria, com a severidade indicada — use julgamento para ajustar para cima/baixo quando o contexto claramente pedir (ex.: um "God Class" de 40 linhas em um script utilitário não é CRITICAL). Sempre justifique a severidade citando a definição correspondente (ver `## Definição de Severidades` no fim deste arquivo).

Cada entrada referencia o padrão de correção equivalente em `refactoring-playbook.md`.

---

### 1. Hardcoded Credentials — CRITICAL

**Definição:** segredos (chaves de API, senhas, tokens, connection strings) embutidos como literais de string no código-fonte, em vez de lidos de variáveis de ambiente/cofre de segredos.

**Sinais de detecção:**
- Atribuições diretas a `SECRET_KEY`, `PASSWORD`, `API_KEY`, `DB_PASS`, `TOKEN` etc. com valor de string literal, não `os.environ.get(...)`/`process.env.X`.
- Strings de alta entropia (parecem hash/chave) próximas de nomes de configuração.
- Credenciais embutidas em connection strings (`postgres://user:senha@host/db`).

**Ver:** `refactoring-playbook.md` #1.

---

### 2. God Class / God Method — CRITICAL

**Definição:** um único arquivo, classe ou função concentra roteamento HTTP, acesso a banco de dados, lógica de negócio e validação para múltiplos domínios — viola completamente a separação de responsabilidades.

**Sinais de detecção:**
- Arquivo/classe grande (regra prática: >150-200 linhas) misturando decorators de rota + queries SQL/ORM + regras de negócio no mesmo escopo.
- Uma única classe/módulo lidando com mais de uma entidade de domínio não relacionada (ex.: usuários E pedidos E pagamentos no mesmo arquivo).
- Construtor/módulo que também é dono da conexão de banco, do schema e dos handlers de rota simultaneamente.

**Ver:** `refactoring-playbook.md` #2.

---

### 3. Confused Deputy — HIGH

**Definição:** um endpoint ou função executa uma ação privilegiada (SQL arbitrário, mutação destrutiva, acesso a dados sensíveis) sem verificar se quem chamou tem autorização — o "deputy" (a aplicação) é enganado a usar seu próprio privilégio em nome de qualquer chamador.

**Sinais de detecção:**
- Rota que executa SQL vindo diretamente do corpo da requisição (`cursor.execute(request.json["sql"])`).
- Rota destrutiva (reset de banco, delete em massa) sem nenhum middleware de autenticação/autorização antes do handler.
- Rota administrativa acessível pelo mesmo path prefix que rotas públicas, sem checagem de role/permissão.

**Ver:** `refactoring-playbook.md` #3.

---

### 4. Spaghetti Code — MEDIUM

**Definição:** fluxo de controle confuso, sem estrutura clara — condicionais profundamente aninhados, callbacks encadeados, funções com múltiplos efeitos colaterais entrelaçados.

**Sinais de detecção:**
- Aninhamento de callbacks ≥3-4 níveis (`db.get(..., (err, row) => { db.run(..., () => { ... }) })`).
- Cadeias de `if/else` aninhadas reimplementando a mesma lógica em vários lugares do arquivo.
- Funções que fazem validação + acesso a dados + resposta HTTP + logging tudo misturado, sem sub-funções nomeadas.

**Ver:** `refactoring-playbook.md` #4.

---

### 5. Lava Flow — LOW

**Definição:** código morto ou obsoleto que permanece no projeto porque ninguém tem certeza se é seguro remover — imports não usados, funções nunca chamadas, dependências declaradas mas nunca importadas, blocos comentados.

**Sinais de detecção:**
- Imports no topo do arquivo nunca referenciados no corpo.
- Dependência no manifesto (ex.: `marshmallow`) sem nenhum `import`/`require` correspondente no código.
- Funções definidas e nunca chamadas em nenhum lugar do projeto.
- Blocos de código comentados deixados no lugar de código antigo.

**Ver:** `refactoring-playbook.md` #5.

---

### 6. SQL Injection — CRITICAL

**Definição:** consultas SQL construídas por concatenação/interpolação de string com entrada do usuário, permitindo que um atacante altere a query.

**Sinais de detecção:**
- Concatenação de string (`"WHERE id = " + str(id)`) ou f-string/`%`-formatting montando SQL com variáveis vindas de `request`.
- Ausência de placeholders parametrizados (`?`, `%s`, `:nome`) em queries que incluem dados de entrada.

**Ver:** `refactoring-playbook.md` #6.

---

### 7. Mutable Global State — HIGH

**Definição:** estado compartilhado mutável em escopo de módulo/processo usado como armazenamento de fato entre requisições, sem persistência real nem controle de concorrência.

**Sinais de detecção:**
- Coleção (`list`/`dict`/objeto) declarada no nível do módulo e mutada dentro de handlers de requisição (`self.notifications.append(...)` num "service" que nunca persiste em banco).
- Cache manual em variável global (`globalCache = {}`) sem expiração nem invalidação.

**Ver:** `refactoring-playbook.md` #7.

---

### 8. Tight Coupling / Ausência de Injeção de Dependência — HIGH

**Definição:** módulos/classes instanciam diretamente suas próprias dependências (conexão de banco, outros serviços) em vez de recebê-las via construtor/parâmetro — impossibilita testar em isolamento ou trocar a implementação.

**Sinais de detecção:**
- `db = sqlite3.connect(...)` ou `new Database(...)` feito dentro da própria classe/função que o usa, em vez de recebido como argumento.
- Uma classe que referencia diretamente outra classe concreta (não uma interface/abstração) para colaborar, sem ponto de injeção.

**Ver:** `refactoring-playbook.md` #8.

---

### 9. N+1 Queries — MEDIUM

**Definição:** uma query que busca uma lista, seguida de uma query adicional por item dentro de um loop, em vez de uma única query em lote/join.

**Sinais de detecção:**
- `for item in lista: Model.query.get(item.algo_id)` — query dentro de loop.
- `.map()`/`forEach` com uma chamada de banco assíncrona por elemento.

**Ver:** `refactoring-playbook.md` #9.

---

### 10. Broken/Weak Cryptography & Fake Auth — CRITICAL

**Definição:** uso de algoritmos criptográficos quebrados/reversíveis para proteger dados sensíveis (senhas, tokens), ou mecanismos de autenticação que não autenticam de fato.

**Sinais de detecção:**
- `hashlib.md5(...)`/`hashlib.sha1(...)` aplicado a senha, sem salt.
- "Hash" caseiro que na verdade é `base64` repetido (reversível, não é hash).
- Senha armazenada ou retornada em texto plano.
- Token de autenticação construído por concatenação previsível (`'fake-jwt-token-' + str(user.id)`) em vez de um JWT assinado de verdade, e/ou nenhuma verificação de token nas rotas ditas "protegidas".

**Ver:** `refactoring-playbook.md` #10.

---

### 11. Bad Naming / Magic Numbers — LOW

**Definição:** identificadores não descritivos ou literais numéricos/string sem nome que controlam comportamento, dificultando leitura e manutenção.

**Sinais de detecção:**
- Variáveis de uma letra fora de loops triviais.
- Números "mágicos" controlando lógica de negócio (limites, status codes, timeouts) sem constante nomeada.

**Ver:** `refactoring-playbook.md` #5 (mesma categoria de limpeza do Lava Flow) e #4.

---

### 12. Silent Error Swallowing — MEDIUM

**Definição:** blocos de tratamento de erro que capturam qualquer exceção e não fazem nada útil com ela (nem logam, nem re-lançam), escondendo falhas reais.

**Sinais de detecção:**
- `except:` genérico (sem tipo) em Python, ou `catch (e) {}` vazio em JS, sem log/re-throw.
- Bloco `try/except` que retorna um valor de sucesso "fake" mesmo quando a exceção indica falha real.

**Ver:** `refactoring-playbook.md` #4.

---

## Detecção de APIs Deprecated (obrigatório)

Sinais específicos de uso de APIs/idiomas obsoletos, cada um com o equivalente moderno recomendado:

| Sinal detectado | Severidade sugerida | Equivalente moderno |
|---|---|---|
| `hashlib.md5`/`hashlib.sha1` para senha | CRITICAL (ver #10) | `werkzeug.security.generate_password_hash` (PBKDF2) ou `bcrypt`/`argon2` |
| `@app.before_first_request` (removido no Flask 2.3+) | MEDIUM | Inicialização no composition root, fora de decorators de request |
| Callback-style (`function(err, data)`) em vez de Promises | MEDIUM | `async`/`await` com Promises nativas |
| `body-parser` como pacote separado no Express | LOW | `express.json()` / `express.urlencoded()` embutidos desde Express 4.16 |
| Sintaxe/idioms de Python 2 (`print "x"`, `except Exception, e`) em base Python 3 | MEDIUM | Sintaxe Python 3 equivalente |
| `flask.ext.<modulo>` (import style antigo) | LOW | `from flask_<modulo> import ...` |
| Criação manual de conexão SQLite por requisição sem pool/context manager | MEDIUM | Pool de conexões ou `with` context manager por request |

---

## Definição de Severidades

- **CRITICAL**: falhas graves de arquitetura ou segurança que impedem o funcionamento correto, expõem dados sensíveis (ex.: credenciais hardcoded, SQL Injection) ou violam completamente a separação de responsabilidades (God Class com banco, lógica complexa e roteamento no mesmo arquivo).
- **HIGH**: fortes violações do padrão MVC ou princípios SOLID que dificultam muito manutenção e testes (lógica de negócio pesada em Controllers, forte acoplamento sem DI, estado global mutável).
- **MEDIUM**: problemas de padronização, duplicação de código ou gargalos de performance moderada (N+1, middlewares mal usados, validações ausentes).
- **LOW**: legibilidade, nomenclatura ruim, magic numbers.

## Checklist de distribuição de severidade (auto-verificação do catálogo)

- CRITICAL: #1, #2, #6, #10 (4 entradas)
- HIGH: #3, #7, #8 (3 entradas)
- MEDIUM: #4, #9, #12 (3 entradas)
- LOW: #5, #11 (2 entradas)

Total: 12 anti-patterns ≥ mínimo de 8 exigido, com as 4 severidades representadas.
