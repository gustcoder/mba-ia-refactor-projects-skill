================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python + Flask 3.0.0
Files:   15 analyzed | ~1158 lines of code

## Summary
CRITICAL: 7 | HIGH: 4 | MEDIUM: 7 | LOW: 6

## Findings

### [CRITICAL] Hardcoded Credentials
File: app.py:13
Description: `SECRET_KEY` está definida como o literal `'super-secret-key-123'` diretamente no código-fonte, em vez de lida de variável de ambiente.
Impact: Qualquer pessoa com acesso ao repositório pode forjar sessões/tokens assinados com essa chave; rotação de segredo exige novo deploy de código.
Recommendation: Ler de `os.environ['SECRET_KEY']`, sem valor default em produção, conforme refactoring-playbook.md #1.

### [CRITICAL] Hardcoded Credentials
File: services/notification_service.py:7-10
Description: Credenciais reais de SMTP (`email_user = 'taskmanager@gmail.com'`, `email_password = 'senha123'`) embutidas como literais no construtor de `NotificationService`.
Impact: Vazamento do repositório expõe credenciais de uma conta de email real, permitindo envio de email em nome da aplicação.
Recommendation: Carregar host/usuário/senha de variáveis de ambiente (`os.environ`), conforme refactoring-playbook.md #1.

### [CRITICAL] Broken/Weak Cryptography & Fake Auth
File: models/user.py:27-32
Description: `set_password`/`check_password` usam `hashlib.md5(pwd.encode()).hexdigest()` sem salt para armazenar e validar senhas de usuário.
Impact: MD5 é criptograficamente quebrado e rápido de forçar por brute-force/rainbow table; um vazamento do banco expõe todas as senhas dos usuários.
Recommendation: Substituir por `werkzeug.security.generate_password_hash`/`check_password_hash` (PBKDF2) ou `bcrypt`, conforme refactoring-playbook.md #10.

### [CRITICAL] Broken/Weak Cryptography & Fake Auth
File: routes/user_routes.py:185-211
Description: `login()` retorna `'token': 'fake-jwt-token-' + str(user.id)` (linha 210) — uma string previsível, não um JWT assinado — e nenhuma rota da aplicação verifica esse token em nenhum momento (não há middleware/decorator de autenticação em nenhum blueprint).
Impact: Qualquer chamador pode forjar o "token" de qualquer usuário (basta saber/adivinhar o `id`) e todas as rotas mutáveis (tasks, users, categories) ficam de fato sem autenticação alguma.
Recommendation: Emitir JWT real assinado (ex.: `flask-jwt-extended`) e validar em todas as rotas protegidas via decorator, conforme refactoring-playbook.md #10.

### [CRITICAL] God Class / God Method
File: routes/task_routes.py:1-300
Description: Blueprint de 300 linhas concentra roteamento HTTP, acesso a banco via `Task.query`/`db.session`, serialização manual campo-a-campo (ex.: linhas 17-28, 162-213) e regras de negócio (cálculo de overdue, validação de status/prioridade/tamanho de título) para a entidade Task, tudo no mesmo arquivo/escopo.
Impact: Qualquer mudança de regra de negócio ou de formato de resposta obriga tocar o mesmo arquivo que trata roteamento; impossível testar validação/serialização isoladamente do Flask.
Recommendation: Extrair camada de serviço (`services/task_service.py`) para regras de negócio e um serializer dedicado para `to_dict`, deixando as rotas como thin controllers — ver mvc-guidelines.md e refactoring-playbook.md #2.

### [CRITICAL] God Class / God Method
File: routes/report_routes.py:1-224
Description: Arquivo de 224 linhas mistura dois domínios não relacionados — geração de relatórios agregados (`summary_report`, `user_report`) e CRUD completo de `Category` (linhas 157-223) — além de lógica de negócio pesada (cálculo de overdue, completion rate) embutida diretamente nos handlers HTTP.
Impact: Mudanças no CRUD de categorias arriscam quebrar a geração de relatórios (e vice-versa) por estarem no mesmo módulo; dificulta reuso da lógica de agregação fora de um contexto HTTP.
Recommendation: Mover CRUD de categoria para `routes/category_routes.py` + `services/category_service.py`; extrair agregações de relatório para `services/report_service.py`, conforme mvc-guidelines.md e refactoring-playbook.md #2.

### [CRITICAL] God Class / God Method
File: routes/user_routes.py:1-212
Description: Arquivo de 212 linhas concentra CRUD de usuário, regra de autenticação (`login`, linhas 185-211), validação de email/senha por regex inline (linhas 61-65, 106-107) e serialização manual de tasks do usuário (linhas 161-181), tudo no mesmo blueprint.
Impact: Lógica de autenticação fica acoplada ao mesmo módulo do CRUD administrativo de usuários, dificultando isolar e testar o fluxo de login separadamente.
Recommendation: Extrair `services/user_service.py` (validação, criação, atualização) e um `services/auth_service.py` para login/token, conforme mvc-guidelines.md e refactoring-playbook.md #2.

### [HIGH] Confused Deputy
File: routes/user_routes.py:92-132
Description: `update_user` aceita `data['role']` (linha 119-122) e aplica diretamente em `user.role`, incluindo `'admin'`, sem nenhuma verificação de que quem está chamando a rota já é admin — e não há middleware de autenticação em toda a aplicação que impeça isso.
Impact: Qualquer chamador não autenticado pode promover a própria conta (ou qualquer conta) a `admin` via `PUT /users/<id>`, obtendo privilégios administrativos completos.
Recommendation: Adicionar verificação de autorização (apenas admin pode alterar `role` de terceiros) e autenticação obrigatória via decorator, conforme refactoring-playbook.md #3.

### [HIGH] Confused Deputy
File: routes/user_routes.py:134-151
Description: `delete_user` deleta o usuário e, em cascata, todas as suas tasks (linhas 140-142) sem nenhuma checagem de autenticação/autorização — a rota destrutiva está no mesmo path prefix público das demais, sem proteção.
Impact: Qualquer chamador pode apagar permanentemente qualquer usuário e todo o seu histórico de tasks sem estar autenticado.
Recommendation: Exigir autenticação + autorização (dono da conta ou admin) antes de permitir a exclusão, conforme refactoring-playbook.md #3.

### [HIGH] Tight Coupling / Ausência de Injeção de Dependência
File: services/notification_service.py:15-20
Description: `send_email` instancia diretamente `smtplib.SMTP(self.email_host, self.email_port)` dentro do próprio método, com host/porta/credenciais fixados no `__init__` da mesma classe — não há ponto de injeção para trocar o cliente de email (ex.: em testes).
Impact: Impossível testar `NotificationService` sem uma conexão SMTP real; trocar de provedor de email exige editar a classe.
Recommendation: Injetar um cliente de email (ou abstração de transporte) via construtor, conforme refactoring-playbook.md #8.

### [HIGH] Mutable Global State
File: services/notification_service.py:6, 31-36, 43-48
Description: `self.notifications` é uma lista em memória (linha 6) usada como "armazenamento de fato" das notificações — `notify_task_assigned` faz `.append(...)` (linhas 31-36) e `get_notifications` lê dela (linhas 43-48) — nada é persistido em banco.
Impact: Todas as notificações são perdidas a cada restart do processo; em múltiplas instâncias/workers, cada uma veria um histórico diferente e incompleto.
Recommendation: Persistir notificações em uma tabela própria via SQLAlchemy, em vez de estado em memória, conforme refactoring-playbook.md #7.

### [MEDIUM] Spaghetti Code
File: models/task.py:50-60
Description: A lógica de "task atrasada" (`due_date` no passado E status não é `done`/`cancelled`) é implementada como condicionais aninhados em `is_overdue()`, mas é **reimplementada** de forma idêntica e independente em routes/task_routes.py:30-39 e 71-80, routes/report_routes.py:33-43 e 132-135, e routes/user_routes.py:171-180 — nenhum desses lugares chama `task.is_overdue()`.
Impact: Uma mudança na regra de "atrasado" (ex.: considerar timezone) exige editar 6 lugares diferentes; divergência entre eles já é possível hoje sem que ninguém perceba.
Recommendation: Centralizar a regra em `Task.is_overdue()` e chamá-la de todos os pontos de serialização/agregação, conforme refactoring-playbook.md #4.

### [MEDIUM] N+1 Queries
File: routes/task_routes.py:16-58
Description: `get_tasks()` busca todas as tasks (linha 14) e, dentro do loop, executa `User.query.get(t.user_id)` (linha 42) e `Category.query.get(t.category_id)` (linha 51) para cada task individualmente.
Impact: Uma listagem de N tasks gera até 1 + 2N queries ao banco; com centenas de tasks a latência do endpoint cresce linearmente e desnecessariamente.
Recommendation: Usar `join`/`joinedload` do SQLAlchemy para trazer `user`/`category` na mesma query, conforme refactoring-playbook.md #9.

### [MEDIUM] N+1 Queries
File: routes/report_routes.py:53-68
Description: `summary_report()` busca todos os usuários (linha 53) e, para cada um, executa `Task.query.filter_by(user_id=u.id).all()` dentro do loop (linha 56) para calcular produtividade.
Impact: Com M usuários, gera 1 + M queries adicionais só para o bloco `user_productivity`, degradando o endpoint de relatório à medida que a base cresce.
Recommendation: Agregar com uma única query usando `GROUP BY`/`func.count` por `user_id`, conforme refactoring-playbook.md #9.

### [MEDIUM] N+1 Queries
File: routes/report_routes.py:157-165
Description: `get_categories()` busca todas as categorias (linha 159) e, para cada uma, executa `Task.query.filter_by(category_id=c.id).count()` dentro do loop (linha 163).
Impact: Mesma degradação linear do endpoint `/categories` conforme o número de categorias cresce.
Recommendation: Substituir por uma única query agregada (`GROUP BY category_id`), conforme refactoring-playbook.md #9.

### [MEDIUM] Silent Error Swallowing
File: routes/report_routes.py:182-188, 204-209, 217-223
Description: `create_category`, `update_category` e `delete_category` usam `except:` genérico que apenas faz rollback e retorna um erro fixo, sem logar a exceção original em nenhum dos três handlers.
Impact: Falhas reais de banco (constraint violation, conexão perdida, etc.) ficam indistinguíveis umas das outras nos logs, dificultando diagnóstico em produção.
Recommendation: Capturar exceção específica, logar com stack trace, e só então responder erro genérico ao cliente, conforme refactoring-playbook.md #4.

### [MEDIUM] Silent Error Swallowing
File: routes/task_routes.py:13-63, 217-223, 231-238
Description: `get_tasks` usa `except:` genérico sem log (linhas 62-63); `update_task` captura `except Exception as e` (linha 221) mas nunca usa/loga `e`; `delete_task` usa `except:` genérico sem log (linhas 236-238).
Impact: Erros inesperados nesses três endpoints não deixam rastro algum, tornando incidentes em produção difíceis de reproduzir ou diagnosticar.
Recommendation: Logar a exceção capturada (`logging.exception(e)`) antes de responder, conforme refactoring-playbook.md #4.

### [MEDIUM] Silent Error Swallowing
File: routes/user_routes.py:127-132, 144-151
Description: `update_user` e `delete_user` usam `except:` genérico que apenas faz rollback e retorna erro fixo, sem logar a causa real da falha.
Impact: Impossível diferenciar, pelos logs, entre um erro de constraint de unicidade de email e uma falha de conexão com o banco, por exemplo.
Recommendation: Logar a exceção específica antes do rollback, conforme refactoring-playbook.md #4.

### [LOW] Lava Flow
File: services/notification_service.py:1-49
Description: A classe `NotificationService` inteira (envio de email, notificação de atribuição/atraso) nunca é importada nem instanciada em nenhum outro arquivo do projeto — é código morto completo.
Impact: Mantém credenciais reais de SMTP hardcoded (ver finding CRITICAL correspondente) e lógica não testada/não usada no repositório, aumentando a superfície de auditoria sem benefício.
Recommendation: Remover se de fato não usado, ou integrar de fato ao fluxo de criação/atualização de task, conforme refactoring-playbook.md #5.

### [LOW] Lava Flow
File: utils/helpers.py:1-117
Description: De 9 funções definidas, apenas `format_date` e `calculate_percentage` são usadas (em routes/report_routes.py); `validate_email`, `sanitize_string`, `generate_id`, `log_action`, `parse_date`, `is_valid_color` e `process_task_data` nunca são chamadas em lugar nenhum, assim como as 7 constantes no final do arquivo (`VALID_STATUSES`, `VALID_ROLES`, `MAX_TITLE_LENGTH`, etc., linhas 110-116); os imports `os`, `sys`, `math`, `hashlib` (linhas 3,5,6,7) também não são referenciados em nenhum ponto do arquivo.
Impact: Regras de validação (tamanho de título, roles válidos, prioridade default) existem duplicadas e hardcoded em routes/task_routes.py e routes/user_routes.py em vez de reusar essas constantes já definidas, gerando risco real de divergência.
Recommendation: Remover o que é de fato morto, e substituir os literais duplicados em routes/ pelas constantes já existentes aqui, conforme refactoring-playbook.md #5.

### [LOW] Lava Flow
File: routes/task_routes.py:7
Description: `import json, os, sys, time` — nenhum dos quatro módulos é referenciado em nenhum ponto do arquivo.
Impact: Ruído de leitura; sugere dependências que não existem de fato, confundindo quem lê o arquivo pela primeira vez.
Recommendation: Remover os imports não usados, conforme refactoring-playbook.md #5.

### [LOW] Lava Flow
File: routes/report_routes.py:8; routes/user_routes.py:6
Description: `import json` em report_routes.py nunca é referenciado; em user_routes.py, `import hashlib, json, re` inclui `hashlib` e `json` sem uso (apenas `re` é de fato usado, para validar email).
Impact: Mesmo problema de ruído/confusão sobre dependências reais do módulo.
Recommendation: Remover os imports não usados, conforme refactoring-playbook.md #5.

### [LOW] Lava Flow
File: requirements.txt:4-6
Description: `marshmallow==3.20.1`, `requests==2.31.0` e `python-dotenv==1.0.0` estão declaradas no manifesto mas nenhuma é importada em nenhum arquivo `.py` do projeto.
Impact: Instala dependências desnecessárias (superfície de supply-chain maior que o necessário) e sugere falsamente que há validação de schema (marshmallow) ou carregamento de `.env` (dotenv), que na verdade não acontecem.
Recommendation: Remover do manifesto, ou efetivamente adotar `python-dotenv` para carregar `SECRET_KEY`/credenciais de ambiente (ver findings de Hardcoded Credentials), conforme refactoring-playbook.md #5.

### [LOW] Bad Naming / Magic Numbers
File: routes/report_routes.py:24-28
Description: Contadores de prioridade nomeados `p1, p2, p3, p4, p5` (mapeados depois para `'critical'`..`'minimal'`) em vez de nomes descritivos; o range válido de prioridade (`1` a `5`) é um literal mágico repetido sem constante nomeada em models/task.py:46, routes/task_routes.py:113-114 e 182-183, apesar de já existir espaço para isso em utils/helpers.py.
Impact: Leitura do bloco exige contar mentalmente "p1 = crítica, p2 = alta..."; qualquer mudança na escala de prioridade (ex.: adicionar prioridade 6) exige caçar todos os literais `1`/`5` espalhados pelo código.
Recommendation: Nomear os contadores por rótulo de prioridade e extrair `PRIORITY_MIN`/`PRIORITY_MAX` como constantes reusadas, conforme refactoring-playbook.md #5.

================================
Total: 24 findings
================================
