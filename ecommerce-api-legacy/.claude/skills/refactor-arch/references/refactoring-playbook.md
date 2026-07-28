# Playbook de Refatoração (Fase 3)

Padrões concretos de transformação, um por anti-pattern do catálogo (`anti-pattern-catalog.md`). Os exemplos usam sintaxe Python/Flask como pseudocódigo de referência — aplique a mesma *forma* de transformação na linguagem/framework real do projeto-alvo (a nota "Aplicação em outras stacks" de cada padrão explica como).

---

## Pattern 1: Hardcoded Credentials → Configuração via variável de ambiente

**Aplica-se a:** anti-pattern-catalog.md #1

**Antes:**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
DEBUG = True
```

**Depois:**
```python
# config/settings.py
import os

SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG = os.environ.get("DEBUG", "false").lower() == "true"
```

**Notas:** valor real do segredo vive só em `.env` (nunca commitado — adicione `.env.example` com chaves vazias como documentação). Em Node/Express: `process.env.SECRET_KEY` + pacote `dotenv`. Em qualquer stack: falhar explicitamente (não usar default silencioso) se o segredo não estiver definido em produção.

---

## Pattern 2: God Class/File → Split por domínio (Model + Controller + Route)

**Aplica-se a:** anti-pattern-catalog.md #2

**Antes:**
```python
# models.py (314 linhas cobrindo produtos, usuarios, pedidos, itens_pedido)
def get_produto(id):
    ...
def criar_usuario(dados):
    ...
def get_pedidos_usuario(usuario_id):
    ...
```

**Depois:**
```python
# models/produto.py
def get_produto(id): ...

# models/usuario.py
def criar_usuario(dados): ...

# models/pedido.py
def get_pedidos_usuario(usuario_id): ...
```

**Notas:** um arquivo por entidade de domínio, cada um só com queries/regras daquela entidade. Em Express: dividir um `AppManager.js` que mistura DB+rotas+handlers em `models/*.js` (acesso a dados) + `routes/*.js` (registro de rota) + `controllers/*.js` (orquestração), removendo a classe única "faz-tudo".

---

## Pattern 3: Confused Deputy → Middleware de autenticação/autorização

**Aplica-se a:** anti-pattern-catalog.md #3

**Antes:**
```python
@app.route("/admin/reset-db", methods=["POST"])
def reset_database():
    db.execute("DELETE FROM produtos")
    db.execute("DELETE FROM usuarios")
    return {"status": "ok"}

@app.route("/admin/query", methods=["POST"])
def run_query():
    sql = request.json["sql"]
    return db.execute(sql).fetchall()
```

**Depois:**
```python
# middlewares/auth.py
def require_admin(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if not current_user_has_role("admin"):
            abort(403)
        return f(*args, **kwargs)
    return wrapper

# routes/admin_routes.py
@app.route("/admin/reset-db", methods=["POST"])
@require_admin
def reset_database():
    return admin_controller.reset_database()
```

**Notas:** o endpoint de SQL arbitrário (`/admin/query`) deve ser removido, não apenas protegido — executar SQL vindo do corpo da requisição é inseguro mesmo com auth. Em qualquer stack: nenhuma rota destrutiva/administrativa deve existir sem um middleware de auth explícito na cadeia antes do handler.

---

## Pattern 4: Spaghetti Code (callbacks/condicionais aninhados) → Flatten

**Aplica-se a:** anti-pattern-catalog.md #4 e #12

**Antes:**
```javascript
db.get(userQuery, (err, user) => {
  if (!err) {
    db.run(insertEnrollment, () => {
      db.get(paymentQuery, (err2, payment) => {
        // 4+ níveis de aninhamento, lógica de negócio misturada
      });
    });
  }
});
```

**Depois:**
```javascript
async function checkout(userId, courseId) {
  const user = await db.get(userQuery, userId);
  await db.run(insertEnrollment, user.id, courseId);
  const payment = await processPayment(user, courseId);
  return payment;
}
```

**Notas:** `async`/`await` substitui a pirâmide de callbacks; cada etapa vira uma linha sequencial, com `try/catch` explícito (nunca `catch (e) {}` vazio — trate ou logue e relance). Em Python: substituir cadeias de `if/else` aninhadas por early returns e funções auxiliares nomeadas.

---

## Pattern 5: Lava Flow (código morto / dependência não usada) → Remoção

**Aplica-se a:** anti-pattern-catalog.md #5 e #11

**Antes:**
```python
import json, os, sys, time  # nenhum destes é usado no arquivo
from marshmallow import Schema  # declarado em requirements.txt, nunca importado em nenhum lugar
```

**Depois:**
```python
# imports não usados removidos; marshmallow removido de requirements.txt
# (ou, se serialização estruturada for desejada, efetivamente adotado com um Schema por entidade)
```

**Notas:** antes de remover uma dependência do manifesto, confirme com uma busca no projeto inteiro que nenhum arquivo a importa. Nomes mágicos/números soltos identificados durante a auditoria (anti-pattern #11) são extraídos para constantes nomeadas no mesmo passo de limpeza.

---

## Pattern 6: SQL Injection → Queries parametrizadas

**Aplica-se a:** anti-pattern-catalog.md #6

**Antes:**
```python
def get_produto(id):
    query = "SELECT * FROM produtos WHERE id = " + str(id)
    return db.execute(query).fetchone()
```

**Depois:**
```python
def get_produto(id):
    query = "SELECT * FROM produtos WHERE id = ?"
    return db.execute(query, (id,)).fetchone()
```

**Notas:** todo dado vindo de fora do processo (`request`, `body`, `params`) que entra numa query deve passar por placeholder parametrizado (`?`/`%s`/`:nome`), nunca concatenação/f-string. Em Node: `db.get("... WHERE id = ?", [id], callback)`. ORMs (SQLAlchemy, Sequelize) fazem isso automaticamente quando se usa o query builder em vez de SQL cru.

---

## Pattern 7: Mutable Global State → Estado persistido/injetado

**Aplica-se a:** anti-pattern-catalog.md #7

**Antes:**
```python
class NotificationService:
    def __init__(self):
        self.notifications = []  # perdido a cada restart, não thread-safe

    def notify(self, msg):
        self.notifications.append(msg)
```

**Depois:**
```python
class NotificationService:
    def __init__(self, db_session):
        self.db = db_session  # injetado, não global

    def notify(self, msg):
        self.db.add(NotificationRecord(message=msg))
        self.db.commit()
```

**Notas:** o estado passa a viver em algo persistido (banco, cache externo com TTL) e a instância do service recebe suas dependências via construtor em vez de guardar estado mutável de módulo. Em Node: substituir `let globalCache = {}` no topo do arquivo por um cache injetado (ex.: cliente Redis passado no construtor).

---

## Pattern 8: Tight Coupling / Ausência de DI → Injeção de dependência

**Aplica-se a:** anti-pattern-catalog.md #8

**Antes:**
```python
class PedidoController:
    def __init__(self):
        self.db = sqlite3.connect("loja.db")  # instanciado internamente
```

**Depois:**
```python
class PedidoController:
    def __init__(self, db_connection):
        self.db = db_connection  # recebido de fora
```

```python
# app.py (composition root)
db_connection = create_connection(settings.DATABASE_URL)
pedido_controller = PedidoController(db_connection)
```

**Notas:** só o composition root (`app.py`/`app.js`) instancia conexões/serviços concretos; todo o resto os recebe por parâmetro. Isso torna a classe testável com um double/mock no lugar da conexão real.

---

## Pattern 9: N+1 Queries → Batch/join

**Aplica-se a:** anti-pattern-catalog.md #9

**Antes:**
```python
tasks = Task.query.all()
for task in tasks:
    task.user = User.query.get(task.user_id)  # 1 query por task
```

**Depois:**
```python
tasks = Task.query.options(joinedload(Task.user)).all()  # 1 query só
```

**Notas:** em SQL cru, o equivalente é um `JOIN` explícito trazendo todos os campos necessários numa única query em vez de um loop com query por item. Em Node com queries manuais: buscar todos os IDs primeiro e fazer uma única query `WHERE id IN (...)`.

---

## Pattern 10: Broken Crypto / Fake Auth → Hash forte + autenticação real

**Aplica-se a:** anti-pattern-catalog.md #10

**Antes:**
```python
import hashlib
def hash_senha(senha):
    return hashlib.md5(senha.encode()).hexdigest()

def login(email, senha):
    ...
    return {"token": "fake-jwt-token-" + str(user.id)}
```

**Depois:**
```python
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

def hash_senha(senha):
    return generate_password_hash(senha)  # PBKDF2 com salt

def login(email, senha):
    user = find_user(email)
    if not user or not check_password_hash(user.senha_hash, senha):
        abort(401)
    token = jwt.encode({"sub": user.id, "exp": ...}, settings.SECRET_KEY, algorithm="HS256")
    return {"token": token}
```

**Notas:** rotas "protegidas" precisam de um middleware que de fato valida o token (assinatura + expiração), não apenas checa se uma string começa com um prefixo. Em Node: `bcrypt.hash`/`bcrypt.compare` + biblioteca `jsonwebtoken` com verificação real via middleware antes do handler.

---

## Checklist de cobertura

Todos os 12 anti-patterns do catálogo têm um padrão de correção correspondente acima (Patterns 1-10, com #4 e #5 cobrindo duas entradas cada). Ao aplicar a Fase 3, use a ordem CRITICAL → HIGH → MEDIUM → LOW definida em `SKILL.md`, mapeando cada finding do relatório ao Pattern correspondente por número.
