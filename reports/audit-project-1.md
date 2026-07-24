================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~780 lines of code

## Summary
CRITICAL: 8 | HIGH: 3 | MEDIUM: 4 | LOW: 3

## Findings

### [CRITICAL] Hardcoded Credentials
File: app.py:7
Description: `app.config["SECRET_KEY"]` é definida como o literal de string `"minha-chave-super-secreta-123"` diretamente no código-fonte, junto com `DEBUG = True` fixo (linha 8).
Impact: Qualquer pessoa com acesso ao repositório pode forjar sessões/tokens assinados com essa chave; `DEBUG=True` fixo também vaza stack traces em produção.
Recommendation: Ler de `os.environ["SECRET_KEY"]` sem default, e `DEBUG` de variável de ambiente com default `false`, conforme `refactoring-playbook.md` #1.

### [CRITICAL] Confused Deputy
File: app.py:59-78
Description: A rota `/admin/query` (`executar_query`) recebe uma string SQL arbitrária no corpo da requisição (`dados.get("sql", "")`) e a executa diretamente via `cursor.execute(query)`, sem nenhuma autenticação/autorização e sem qualquer restrição sobre o que pode ser executado.
Impact: Qualquer chamador não autenticado pode ler todas as tabelas (incluindo senhas em texto plano — ver finding de Broken Crypto), alterar ou apagar dados livremente (`DROP TABLE`, `UPDATE` arbitrário) — equivalente a controle total do banco de dados. Isso excede o caso-base do catálogo (rota destrutiva sem auth) porque a ação não é limitada a um conjunto conhecido de operações, e sim SQL arbitrário — por isso a severidade foi elevada de HIGH (baseline do catálogo) para CRITICAL, conforme a definição de CRITICAL em `anti-pattern-catalog.md` ("expõem dados sensíveis... ou violam completamente a separação de responsabilidades").
Recommendation: Remover completamente o endpoint (não apenas protegê-lo com auth) — ver nota de `refactoring-playbook.md` #3: "o endpoint de SQL arbitrário deve ser removido, não apenas protegido".

### [CRITICAL] Hardcoded Credentials
File: controllers.py:289
Description: O handler `health_check` inclui `"secret_key": "minha-chave-super-secreta-123"` no corpo da resposta JSON de uma rota pública (`/health`, sem autenticação).
Impact: Além de estar hardcoded no código-fonte, o segredo é ativamente exposto pela API a qualquer chamador não autenticado, ampliando a superfície de ataque além do repositório.
Recommendation: Nunca incluir segredos de configuração em respostas de API; `health_check` deve reportar apenas status operacional (ex.: `"database": "connected"`), conforme `refactoring-playbook.md` #1.

### [CRITICAL] God Class / God Method
File: controllers.py:1-293
Description: Um único arquivo de 293 linhas concentra os handlers de 4 domínios não relacionados (produtos, usuários, pedidos, relatórios), cada um duplicando o mesmo padrão de validação manual, formatação de resposta e `print` de log, sem nenhuma separação por entidade.
Impact: Qualquer mudança em um domínio (ex.: regra de validação de produto) exige navegar o mesmo arquivo dos demais domínios; impossível testar ou versionar um domínio isoladamente.
Recommendation: Separar em `controllers/produto_controller.py`, `controllers/usuario_controller.py`, `controllers/pedido_controller.py`, conforme `mvc-guidelines.md` (SRP) e `refactoring-playbook.md` #2.

### [CRITICAL] God Class / God Method
File: models.py:1-315
Description: Um único arquivo de 315 linhas concentra todo o acesso a dados de 4 entidades não relacionadas (produtos, usuários, pedidos, itens_pedido), com queries SQL cruas construídas por concatenação de string em praticamente todas as funções.
Impact: Acoplamento total entre entidades no mesmo módulo; qualquer alteração de schema de uma entidade arrisca quebrar as demais; impossível testar uma entidade isoladamente.
Recommendation: Separar em `models/produto.py`, `models/usuario.py`, `models/pedido.py`, conforme `mvc-guidelines.md` (SRP) e `refactoring-playbook.md` #2.

### [CRITICAL] SQL Injection
File: models.py:24-297
Description: Praticamente toda função de acesso a dados constrói SQL por concatenação de string com dados de entrada não sanitizados, sem placeholders parametrizados: `get_produto_por_id` (linha 28), `criar_produto` (47-50, concatenando `nome`/`descricao`/`categoria` vindos direto do request), `atualizar_produto` (57-61), `deletar_produto` (linha 68), `get_usuario_por_id` (linha 92), `criar_usuario` (126-129), `criar_pedido` (140, 148-151, 157-161, 163-166), `get_pedidos_usuario` (174, 188, 192), `get_todos_pedidos` (206, 220, 224), `atualizar_status_pedido` (279-281) e `buscar_produtos` (291-297, onde o termo de busca `termo` entra sem escape em uma cláusula `LIKE`).
Impact: Um atacante pode injetar SQL arbitrário via qualquer campo de texto (nome de produto, termo de busca, etc.) para ler, alterar ou apagar dados fora do escopo pretendido da query original.
Recommendation: Substituir toda concatenação por queries parametrizadas (`?`) em todas as funções listadas, conforme `refactoring-playbook.md` #6.

### [CRITICAL] SQL Injection
File: models.py:105-120
Description: `login_usuario` monta a query de autenticação por concatenação direta: `"SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"` (linhas 109-111), usando `email`/`senha` vindos sem qualquer validação do corpo da requisição.
Impact: Um atacante pode fazer bypass completo de autenticação com um payload como `' OR '1'='1' --` no campo email ou senha, autenticando-se como qualquer usuário sem conhecer a senha — destacado separadamente por ser o caso de maior impacto (bypass de auth) entre as ocorrências de SQL Injection do arquivo.
Recommendation: Query parametrizada (`?`) para email/senha, combinada com hashing de senha (ver finding de Broken Crypto abaixo) — `refactoring-playbook.md` #6 e #10.

### [CRITICAL] Broken/Weak Cryptography & Fake Auth
File: models.py:72-131
Description: Senhas são armazenadas e comparadas em texto plano em todo o arquivo: `get_todos_usuarios` retorna o campo `"senha": row["senha"]` sem mascarar (linha 83), `get_usuario_por_id` faz o mesmo (linha 99), `login_usuario` compara a senha recebida diretamente contra o valor em texto plano do banco sem nenhum hash (linha 110), e `criar_usuario` insere a senha recebida como texto plano sem hashear (linha 128). Não há nenhuma chamada a `hashlib`, `bcrypt`, `werkzeug.security` ou similar em todo o projeto, e `login()` (controllers.py:167-186) não emite token algum após autenticar — apenas devolve o registro do usuário.
Impact: Vazamento do banco (ou da rota `/usuarios`, que não tem auth) expõe todas as senhas dos usuários em claro; sem emissão de token, não há mecanismo real de sessão/autorização para proteger chamadas subsequentes.
Recommendation: Hashear senha com `werkzeug.security.generate_password_hash`/`check_password_hash` (PBKDF2) no cadastro e no login, nunca retornar o campo `senha` em nenhuma resposta, e emitir um JWT assinado real no login, conforme `refactoring-playbook.md` #10.

### [HIGH] Confused Deputy
File: app.py:47-57
Description: A rota `/admin/reset-db` (`reset_database`) apaga todas as linhas de `itens_pedido`, `pedidos`, `produtos` e `usuarios` (linhas 51-54) sem nenhuma verificação de autenticação/autorização antes do handler.
Impact: Qualquer chamador não autenticado pode apagar todo o conteúdo do banco de dados em produção.
Recommendation: Adicionar middleware `require_admin` na cadeia da rota, conforme `refactoring-playbook.md` #3.

### [HIGH] Mutable Global State
File: database.py:4,7-10
Description: `db_connection` é declarada como `None` no escopo do módulo (linha 4) e mutada dentro de `get_db()` (linhas 7-10) para funcionar como uma conexão singleton compartilhada entre todas as requisições, usando `check_same_thread=False` como workaround para o fato de o SQLite normalmente proibir isso entre threads.
Impact: Sem controle de concorrência real, requisições simultâneas podem colidir na mesma conexão/cursor, causando corrupção de estado ou resultados inconsistentes sob carga.
Recommendation: Usar conexão por requisição (context manager) ou um pool de conexões, injetado explicitamente em vez de global de módulo, conforme `refactoring-playbook.md` #7.

### [HIGH] Tight Coupling / Ausência de Injeção de Dependência
File: database.py:4,7 (consumido em todas as funções de models.py e em app.py:49-50,66)
Description: Toda função de `models.py`, além dos handlers administrativos de `app.py`, chama `get_db()` diretamente para obter a conexão global, em vez de recebê-la via parâmetro/construtor — não existe nenhum ponto de injeção de dependência no projeto.
Impact: Impossível testar qualquer função de model isoladamente com um double/mock de banco; qualquer troca de banco de dados exige alterar todos os arquivos que chamam `get_db()`.
Recommendation: Composition root (`app.py`) cria a conexão/pool uma vez e a injeta explicitamente nos controllers/models, conforme `mvc-guidelines.md` (DIP) e `refactoring-playbook.md` #8.

### [MEDIUM] Spaghetti Code
File: controllers.py:24-96
Description: `criar_produto` (24-62) e `atualizar_produto` (64-96) reimplementam bloco a bloco a mesma sequência de validação manual (`nome`/`preco`/`estoque` obrigatórios, preço/estoque não-negativos) em vez de compartilhar uma função de validação comum.
Impact: Qualquer alteração de regra de validação (ex.: novo campo obrigatório) precisa ser replicada manualmente em ambos os lugares, com alto risco de divergência entre criação e atualização.
Recommendation: Extrair a validação para uma função/Model compartilhada, conforme `refactoring-playbook.md` #4.

### [MEDIUM] Silent Error Swallowing
File: controllers.py:21-22,95-96,108-109,125-126,133-134,143-144,226-227,234-235,254-255,261-262,291-292
Description: A grande maioria dos handlers usa `except Exception as e: return jsonify({"erro": str(e)}), 500` sem nenhum log — ex.: `buscar_produto` (21-22), `atualizar_produto` (95-96), `deletar_produto` (108-109), `buscar_produtos` (125-126), `listar_usuarios` (133-134), `buscar_usuario` (143-144), `listar_pedidos_usuario` (226-227), `listar_todos_pedidos` (234-235), `atualizar_status_pedido` (254-255), `relatorio_vendas` (261-262) e `health_check` (291-292). Apenas `listar_produtos`, `criar_produto` e `criar_pedido` ao menos fazem `print` do erro antes de retornar.
Impact: Falhas reais (erro de banco, exceção inesperada) não deixam nenhum rastro server-side na maioria dos endpoints, dificultando diagnóstico em produção.
Recommendation: Handler de erro centralizado (middleware) que loga toda exceção antes de responder, conforme `refactoring-playbook.md` #4.

### [MEDIUM] Detecção de APIs Deprecated — Conexão SQLite manual sem pool/context manager
File: database.py:7-10
Description: A conexão SQLite é criada manualmente uma única vez como global (`sqlite3.connect(db_path, check_same_thread=False)`) e reutilizada por todas as requisições, em vez de usar um pool de conexões ou `with` context manager por request.
Impact: Sem um pool/gerenciamento por request, conexões não são liberadas/recicladas corretamente, e o `check_same_thread=False` mascara um problema real de concorrência em vez de resolvê-lo.
Recommendation: Adotar `with sqlite3.connect(...) as conn:` por requisição ou um pool de conexões, conforme tabela de "Detecção de APIs Deprecated" em `anti-pattern-catalog.md`.

### [MEDIUM] N+1 Queries
File: models.py:139-166,171-233
Description: `criar_pedido` executa uma query SELECT por item dentro do loop de validação (linha 140) e depois mais uma query por item para buscar o preço novamente (linha 155) em vez de reaproveitar o resultado já obtido; `get_pedidos_usuario` e `get_todos_pedidos` fazem uma query de itens por pedido (188/220) e, dentro desse loop, mais uma query de produto por item (192/224) — uma cascata de N+1 queries em vez de um JOIN único.
Impact: Tempo de resposta cresce linearmente com o número de itens/pedidos, degradando significativamente sob volume de dados maior.
Recommendation: Substituir por uma única query com `JOIN` trazendo pedidos + itens + produtos de uma vez, conforme `refactoring-playbook.md` #9.

### [LOW] Bad Naming / Magic Numbers
File: controllers.py:47-52
Description: Limites de validação usam números mágicos sem constante nomeada (`len(nome) < 2`, `len(nome) > 200`, linhas 47-50) e a lista de categorias válidas é um literal inline (`categorias_validas = [...]`, linha 52) duplicável em outros lugares do código; o parâmetro `id` (usado em `buscar_produto`, `atualizar_produto`, `deletar_produto` e em várias funções de `models.py`) também sombreia o builtin `id()` do Python.
Impact: Limites de validação e listas de valores válidos ficam espalhados e sem nome, dificultando manutenção consistente; sombrear `id()` pode causar bugs sutis se o builtin for necessário no mesmo escopo.
Recommendation: Extrair para constantes nomeadas (`NOME_MIN_LEN`, `NOME_MAX_LEN`, `CATEGORIAS_VALIDAS`) e renomear o parâmetro para `produto_id`/`usuario_id`, conforme `refactoring-playbook.md` #5.

### [LOW] Lava Flow
File: database.py:2
Description: `import os` nunca é referenciado em nenhum lugar do arquivo — `db_path` é um literal de string fixo, não lido via `os.environ`.
Impact: Import morto que não comunica nenhuma intenção real do código; ruído de manutenção.
Recommendation: Remover o import não utilizado (ou efetivamente usá-lo para ler `DATABASE_URL`/`db_path` de variável de ambiente), conforme `refactoring-playbook.md` #5.

### [LOW] Lava Flow
File: models.py:2
Description: `import sqlite3` nunca é referenciado no corpo do arquivo — todo acesso a banco passa por `get_db()` de `database.py`, e nenhuma função usa `sqlite3.*` diretamente.
Impact: Import morto sem função no arquivo.
Recommendation: Remover o import não utilizado, conforme `refactoring-playbook.md` #5.

================================
Total: 18 findings
================================
