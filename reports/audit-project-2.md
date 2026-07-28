================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js) + Express 4.22.1
Files:   3 analyzed | ~180 lines of code

## Summary
CRITICAL: 3 | HIGH: 4 | MEDIUM: 4 | LOW: 2

## Findings

### [CRITICAL] Hardcoded Credentials
File: src/utils.js:2-5
Description: Objeto `config` contém `dbPass: "senha_super_secreta_prod_123"`, `paymentGatewayKey: "pk_live_1234567890abcdef"` e `dbUser`/`smtpUser` como literais de string diretamente no código-fonte, em vez de lidos de `process.env`.
Impact: Qualquer pessoa com acesso ao repositório (incluindo histórico do git) tem a chave de produção do gateway de pagamento e a senha do banco; rotação de credenciais exige alterar código-fonte.
Recommendation: Ler todos os valores de `process.env.*` (dotenv em dev), sem default sensível em produção, seguindo `mvc-guidelines.md` para a camada de configuração.

### [CRITICAL] God Class / God Method
File: src/AppManager.js:1-141
Description: A classe `AppManager` concentra em um único arquivo: criação de conexão SQLite, definição de schema (5 tabelas), seed de dados, e os handlers de rota de checkout, relatório financeiro e exclusão de usuário — misturando 4 entidades de domínio não relacionadas (users, courses, enrollments, payments) e todas as camadas (routing HTTP + SQL + regra de negócio) no mesmo escopo.
Impact: Qualquer alteração em uma entidade (ex.: pagamentos) arrisca quebrar checkout, relatório ou schema; impossível testar regras de negócio isoladamente do Express/SQLite.
Recommendation: Separar em models por entidade, controllers por rota e um camada de acesso a dados dedicada, conforme `mvc-guidelines.md`.

### [CRITICAL] Broken/Weak Cryptography & Fake Auth
File: src/utils.js:17-23
Description: `badCrypto()` "hasheia" a senha repetindo `Buffer.from(pwd).toString('base64')` 10000 vezes e truncando o resultado — isso é reversível (base64 não é hash) e usado em produção para armazenar a senha do usuário em `AppManager.js:68-69`.
Impact: Senhas de usuário podem ser decodificadas trivialmente a partir do valor armazenado no banco; nenhuma proteção real contra vazamento de credenciais em caso de dump do banco.
Recommendation: Substituir por `bcrypt`/`argon2` com salt, aplicado na camada de Model/Service de usuário, conforme `refactoring-playbook.md` #10.

### [HIGH] Confused Deputy
File: src/AppManager.js:80
Description: Rota `GET /api/admin/financial-report` expõe receita e dados de todos os alunos/cursos sem nenhum middleware de autenticação/autorização — qualquer chamador não autenticado acessa dados administrativos.
Impact: Vazamento de dados financeiros e pessoais (nomes, valores pagos) para qualquer cliente HTTP não autenticado.
Recommendation: Adicionar middleware de auth + checagem de role admin antes do controller, isolando rotas administrativas conforme `mvc-guidelines.md`.

### [HIGH] Confused Deputy
File: src/AppManager.js:131-137
Description: Rota `DELETE /api/users/:id` executa exclusão destrutiva de usuário sem nenhuma checagem de autenticação/autorização de quem chama, e o próprio comentário no código ("mas as matrículas e pagamentos ficaram sujos no banco") reconhece a ausência de tratamento.
Impact: Qualquer chamador não autenticado pode apagar qualquer usuário do sistema, deixando dados órfãos em `enrollments`/`payments`.
Recommendation: Proteger com middleware de auth/role e mover a exclusão para um Service que trate integridade referencial, conforme `refactoring-playbook.md` #3.

### [HIGH] Mutable Global State
File: src/utils.js:9,12-15 (usado em src/AppManager.js:59)
Description: `globalCache = {}` é um objeto mutável em escopo de módulo, atualizado por `logAndCache()` a cada checkout (`AppManager.js:59`), sem expiração, sem invalidação e sem persistência real — funciona como um "banco de dados" paralelo em memória do processo.
Impact: Estado perdido a cada restart, inconsistente entre múltiplas instâncias/processos (não escala horizontalmente), e cresce indefinidamente (memory leak) sem limpeza.
Recommendation: Remover o cache manual ou substituir por um cache real com TTL (Redis/memória com expiração), fora do módulo de config, conforme `refactoring-playbook.md` #7.

### [HIGH] Tight Coupling / Ausência de Injeção de Dependência
File: src/AppManager.js:4-8
Description: O construtor de `AppManager` instancia diretamente `new sqlite3.Database(':memory:')`, acoplando a classe à implementação concreta do driver SQLite em vez de recebê-la via injeção.
Impact: Impossível testar os handlers de rota com um banco de teste/mock sem monkey-patching; troca de banco de dados exige reescrever a classe inteira.
Recommendation: Receber a conexão/repositório via construtor ou factory, conforme `mvc-guidelines.md` (composition root) e `refactoring-playbook.md` #8.

### [MEDIUM] Spaghetti Code
File: src/AppManager.js:28-78
Description: Handler de `POST /api/checkout` aninha 5+ níveis de callbacks (`db.get` → `db.get` → `processPaymentAndEnroll` → `db.run` → `db.run` → `db.run`), misturando validação, decisão de criar usuário, processamento de pagamento, matrícula, auditoria e resposta HTTP em uma única função sem sub-funções nomeadas fora do próprio handler.
Impact: Fluxo de controle difícil de acompanhar e testar; qualquer novo caso (ex.: cupom de desconto) provavelmente aumenta ainda mais o aninhamento.
Recommendation: Extrair para `async`/`await` com funções nomeadas por etapa (validar, resolver usuário, processar pagamento, matricular, auditar) na camada de Service, conforme `refactoring-playbook.md` #4.

### [MEDIUM] N+1 Queries
File: src/AppManager.js:89-127
Description: Para cada curso retornado por `SELECT * FROM courses` (linha 83), o código dispara `SELECT ... FROM enrollments` (linha 92) dentro de `courses.forEach`, e para cada matrícula dispara mais duas queries (`users` linha 104, `payments` linha 106) dentro de `enrollments.forEach` — N cursos × M matrículas × 2 queries adicionais.
Impact: Para um catálogo com dezenas de cursos e centenas de matrículas, o endpoint dispara centenas/milhares de queries sequenciais, tornando o relatório administrativo lento e sobrecarregando o banco.
Recommendation: Substituir por uma única query com `JOIN` entre `courses`, `enrollments`, `users` e `payments`, agregada na camada de Model, conforme `refactoring-playbook.md` #9.

### [MEDIUM] Silent Error Swallowing
File: src/AppManager.js:133-136
Description: `db.run("DELETE FROM users WHERE id = ?", [id], (err) => { res.send(...) })` recebe `err` no callback mas nunca o verifica — mesmo se a exclusão falhar, a resposta enviada ao cliente é sempre a mensagem de "sucesso".
Impact: Falhas reais de exclusão (ex.: erro de banco, constraint) são reportadas ao cliente como sucesso, mascarando bugs e dificultando debugging em produção.
Recommendation: Checar `err` e retornar status 500 com log apropriado antes de responder sucesso, conforme `refactoring-playbook.md` #4.

### [MEDIUM] Deprecated API — Callback-style em vez de Promises
File: src/AppManager.js:37-136 (todas as chamadas `this.db.get`/`.all`/`.run`)
Description: Toda a camada de acesso a dados usa a API de callback do `sqlite3` (`function(err, data) {}`), o idiom que motivou o aninhamento descrito no finding de Spaghetti Code.
Impact: Impede uso direto de `async`/`await`, forçando aninhamento manual e tratamento de erro repetitivo em cada callback.
Recommendation: Adotar um wrapper com Promises (ex.: `sqlite` + `sqlite3` com `open()`, ou `util.promisify`) na camada de Model/Repository, conforme catálogo de APIs deprecated.

### [LOW] Bad Naming / Magic Numbers
File: src/AppManager.js:29-33
Description: Variáveis do handler de checkout usam nomes de uma/duas letras sem relação óbvia com o domínio: `u`, `e`, `p`, `cid`, `cc` para usuário, email, senha, id do curso e cartão.
Impact: Leitura do handler exige mapear mentalmente cada abreviação; aumenta risco de trocar parâmetros por engano em manutenções futuras.
Recommendation: Renomear para `username`, `email`, `password`, `courseId`, `cardNumber` na camada de Controller/DTO, conforme `mvc-guidelines.md`.

### [LOW] Lava Flow
File: src/utils.js:10 (importado em src/AppManager.js:2)
Description: `totalRevenue` é declarada e exportada em `utils.js`, e importada em `AppManager.js`, mas nunca lida nem atribuída em nenhum ponto do código — é uma variável morta que sugere uma feature de agregação de receita nunca implementada.
Impact: Confunde leitores que assumem que `totalRevenue` reflete algum estado real; sinaliza código morto acumulado.
Recommendation: Remover a variável e o import não utilizado, ou implementar de fato a agregação de receita no Model de pagamentos, conforme `refactoring-playbook.md` #5.

================================
Total: 13 findings
================================
