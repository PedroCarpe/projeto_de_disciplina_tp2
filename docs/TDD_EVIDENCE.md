# Evidência TDD — cadastro do Nossa Rua

Este documento registra o ciclo **RED → GREEN → REFACTOR** aplicado aos comportamentos de
persistência do cadastro. A implementação visual da tela já existia antes desta rodada e
**não** é apresentada como se tivesse sido feita com TDD desde o início.

## Escopo do ciclo

Comportamentos implementados seguindo o ciclo:

1. acessar `/cadastro/` e receber HTTP 200;
2. enviar formulário vazio e exibir erros por campo;
3. rejeitar senhas diferentes;
4. rejeitar e-mail já cadastrado (comparação sem diferenciar maiúsculas);
5. criar usuário com dados válidos, senha com hash e e-mail como `username`;
6. manter o link de login apontando para `/login/`.

## RED — teste antes da implementação

Foram escritos primeiros os testes:

- `CadastroViewTests.test_cadastro_cria_usuario_com_dados_validos`
- `CadastroViewTests.test_cadastro_rejeita_email_duplicado`

Comando executado em `backend/`:

```powershell
.\.venv\Scripts\python.exe manage.py test
```

Saída relevante:

```text
Creating test database for alias 'default'...
F...F...........
======================================================================
FAIL: test_cadastro_cria_usuario_com_dados_validos
AssertionError: False is not true : Couldn't find 'Conta criada com sucesso.' in the following response
======================================================================
FAIL: test_cadastro_rejeita_email_duplicado
AssertionError: False is not true : Couldn't find 'Este e-mail já está cadastrado.' in the following response
----------------------------------------------------------------------
Ran 15 tests

FAILED (failures=2)
```

Nesse momento a view ainda apenas validava e renderizava o formulário: não criava usuário,
não verificava duplicação e não exibia mensagem de sucesso.

## GREEN — implementação mínima

Implementado em `backend/frontend/views.py`:

- verificação de e-mail duplicado com `User.objects.filter(email__iexact=email).exists()`;
- criação do usuário com `User.objects.create_user(username=email, ...)`;
- senha armazenada com hash pelo próprio `create_user`;
- contexto `sucesso` com mensagem `"Conta criada com sucesso. Acesse com seu e-mail e senha."`.

No template `cadastro.html`, foi adicionado o alerta `.aviso-sucesso` com `role="status"`,
usando os tokens já existentes (`--menta`, `--verde-escuro`).

Um teste mais antigo, `test_cadastro_keeps_valid_values_without_errors`, foi renomeado para
`test_cadastro_limpa_formulario_apos_sucesso`: com a criação real do usuário, limpar os campos
após o sucesso passou a ser o comportamento desejado.

Comando executado novamente:

```text
Creating test database for alias 'default'...
...............
----------------------------------------------------------------------
Ran 15 tests in 1.653s

OK
Destroying test database for alias 'default'...
Found 15 test(s).
System check identified no issues (0 silenced).
```

## REFACTOR — melhoria com testes passando

A validação e a criação foram extraídas para funções pequenas em `frontend/views.py`:

- `validar_cadastro(nome, email, senha, confirmacao) -> dict[str, str]`
- `criar_usuario(nome, email, senha) -> None`

A view `cadastro_view` ficou responsável apenas por ler o `POST`, chamar essas funções
e montar o contexto. Nenhuma regra de negócio foi movida para o JavaScript.

Comando executado após o refactor:

```text
Creating test database for alias 'default'...
...............
----------------------------------------------------------------------
Ran 15 tests in 1.653s

OK
Destroying test database for alias 'default'...
Found 15 test(s).
System check identified no issues (0 silenced).
```

## Verificação final

```text
python manage.py check  → System check identified no issues (0 silenced).
ruff check .            → All checks passed!
pytest                  → 15 passed in 2.57s
TOTAL                   → 209 statements, 2 miss, 99% (99.04%)
```

A cobertura ficou acima da meta de 80% definida em `docs/FRONTEND.md`.

## Observação sobre o histórico no GitHub

Esta evidência está sendo commitada **em um único commit**, junto com o código final. Isso é
intencional: o ciclo real aconteceu nesta sessão, mas não foi possível gerar três commits
cronológicos distintos sem reconstruir artificialmente o histórico. Os trechos acima são as
saídas reais dos comandos executados durante o desenvolvimento.
