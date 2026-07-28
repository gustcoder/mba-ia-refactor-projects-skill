# Template do Relatório de Auditoria (Fase 2)

Este é o formato exato a ser preenchido e usado tanto para o stdout quanto para o arquivo salvo em `reports/audit-project-N.md`. O arquivo salvo contém **apenas o relatório** (sem a linha de prompt `[y/n]`, que é só interativa e aparece somente no stdout após o relatório).

A regra de resolução da raiz do repositório e de derivação de `N` está definida em `SKILL.md` — não a redefina aqui.

## Cabeçalho

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: {nome_do_projeto}
Stack:   {linguagem} + {framework}
Files:   {quantidade_arquivos} analyzed | ~{linhas_de_codigo} lines of code
```

- `{nome_do_projeto}`: nome do diretório raiz do projeto-alvo.
- `{linguagem}`/`{framework}`: os mesmos valores detectados na Fase 1.
- `{quantidade_arquivos}`: mesmo número de `Source files:` da Fase 1.

## Resumo

```
## Summary
CRITICAL: {n} | HIGH: {n} | MEDIUM: {n} | LOW: {n}
```

Sempre liste as 4 severidades nesta ordem fixa, mesmo quando a contagem for 0.

## Findings

Um bloco por finding, nesta ordem exata de campos:

```
### [{SEVERIDADE}] {Nome do Anti-Pattern}
File: {caminho/relativo.ext}:{linha ou intervalo de linhas}
Description: {o que está errado, específico desta ocorrência — não a definição genérica do catálogo}
Impact: {consequência concreta se não for corrigido}
Recommendation: {o que fazer, apontando para a camada/padrão alvo do refactoring-playbook.md}
```

**Regras obrigatórias:**
- `File:linha` deve vir de leitura real do arquivo nesta execução — nunca estimado ou copiado de exemplos anteriores.
- Ordene os findings por severidade (CRITICAL primeiro) e, dentro da mesma severidade, por arquivo.
- `{Nome do Anti-Pattern}` deve usar exatamente o nome usado em `anti-pattern-catalog.md`, para rastreabilidade.
- `Description` descreve a instância real encontrada (ex.: "SECRET_KEY hardcoded como 'minha-chave-super-secreta-123'"), não a definição abstrata do anti-pattern.

## Rodapé

```
================================
Total: {N} findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

- `{N}` = soma de todas as severidades do resumo.
- A linha `Phase 2 complete...` e tudo abaixo dela é exibida apenas no stdout, nunca gravada no arquivo salvo.

## Exemplo preenchido (ilustrativo, não copiar valores)

```
================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python + Flask
Files:   4 analyzed | ~800 lines of code

## Summary
CRITICAL: 4 | HIGH: 5 | MEDIUM: 2 | LOW: 3

## Findings

### [CRITICAL] God Class / God Method
File: models.py:1-314
Description: Arquivo único contém toda a lógica de acesso a dados, queries SQL e formatação para 4 domínios diferentes (produtos, usuários, pedidos, itens de pedido).
Impact: Impossível testar em isolamento; qualquer mudança em um domínio arrisca quebrar os outros três.
Recommendation: Separar em um model por domínio (models/produto.py, models/usuario.py, ...), conforme mvc-guidelines.md.

### [CRITICAL] Hardcoded Credentials
File: app.py:7
Description: SECRET_KEY definida como literal de string 'minha-chave-super-secreta-123' diretamente no código.
Impact: Qualquer pessoa com acesso ao repositório pode forjar sessões/tokens assinados com essa chave.
Recommendation: Ler de variável de ambiente (os.environ["SECRET_KEY"]), sem valor default em produção.

================================
Total: 14 findings
================================

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```
