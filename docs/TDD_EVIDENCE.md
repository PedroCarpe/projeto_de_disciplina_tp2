# Evidência TDD — Nossa Rua (cadastro e login)

Este documento registra o ciclo **RED → GREEN → REFACTOR** aplicado aos comportamentos de
persistência do cadastro. A implementação visual da tela já existia antes desta rodada e
**não** é apresentada como se tivesse sido feita com TDD desde o início.

## Escopo da funcionalidade e comportamentos exercitados

Comportamentos exercitados pela funcionalidade de cadastro:

1. acessar `/cadastro/` e receber HTTP 200;
2. enviar formulário vazio e exibir erros por campo;
3. rejeitar senhas diferentes;
4. rejeitar e-mail inválido;
5. criar usuário com dados válidos, senha com hash e e-mail como `username`;
6. rejeitar e-mail já cadastrado (comparação sem diferenciar maiúsculas);
7. manter o link de login apontando para `/login/`.

**O ciclo RED → GREEN → REFACTOR documentado abaixo concentra-se apenas nos itens 5 e 6**
(criação de usuário e rejeição de e-mail duplicado). Os demais comportamentos já estavam
implementados e testados antes desta rodada; não são apresentados como TDD.

## RED — testes antes da implementação

Foram escritos primeiro os dois testes abaixo, **já com as asserções de persistência**.

`CadastroViewTests.test_cadastro_cria_usuario_com_dados_validos`:

```python
resposta = self.client.post(
    reverse("cadastro"),
    {
        "nome": "Maria Silva",
        "email": "maria@exemplo.com",
        "senha": "senhaSegura123",
        "confirmacao_senha": "senhaSegura123",
    },
)

self.assertEqual(resposta.status_code, 200)
self.assertContains(resposta, "Conta criada com sucesso.")

usuario = User.objects.get(email="maria@exemplo.com")
self.assertEqual(usuario.username, "maria@exemplo.com")
self.assertEqual(usuario.get_full_name(), "Maria Silva")
self.assertTrue(usuario.check_password("senhaSegura123"))
self.assertNotEqual(usuario.password, "senhaSegura123")
```

`CadastroViewTests.test_cadastro_rejeita_email_duplicado`:

```python
User.objects.create_user(
    username="joao@exemplo.com",
    email="joao@exemplo.com",
    password="senhaAntiga123",
)

resposta = self.client.post(
    reverse("cadastro"),
    {
        "nome": "Outro Joao",
        "email": "JOAO@exemplo.com",
        "senha": "senhaNova123",
        "confirmacao_senha": "senhaNova123",
    },
)

self.assertEqual(resposta.status_code, 200)
self.assertContains(resposta, "Este e-mail já está cadastrado.")
self.assertEqual(User.objects.count(), 1)
```

As consultas `User.objects.get(...)` e `check_password(...)` vão além de um simples
`User.objects.filter(email=...).exists()`: confirmam também `username`, nome e hash da senha.
Já `assertEqual(User.objects.count(), 1)` garante que o segundo cadastro não incrementou o banco.
Essas asserções estavam presentes no
estado RED, mas **não foram avaliadas** naquela execução: o `assertContains` da linha anterior
falhou primeiro. Por isso a saída registrada mostra apenas mensagens ausentes — não é uma
prova direta de ausência de persistência, e o documento não a apresenta como tal. A regra passou
a ser exercitada diretamente quando os testes ficaram verdes no GREEN.

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

A execução registrada após o refactor produziu exatamente a mesma saída da etapa GREEN
(`Ran 15 tests in 1.653s`). Como não existe uma segunda saída distinta preservada, não a repito
aqui como evidência independente. O refactor foi validado por `ruff check .` naquela rodada e
pela execução final registrada em **Verificação final**, com a suíte já ampliada para 19 testes.

## Login — ciclo aplicado a um comportamento ausente

A tela de login já existia antes desta rodada. Para não apresentá-la como se tivesse nascido de
TDD, o ciclo abaixo foi aplicado apenas a um comportamento que **ainda faltava**: marcar a opção
ativa do alternador com `aria-current="page"`, como já fazia o cadastro.

### RED

Teste escrito primeiro em `frontend/test_views.py`:

- `LoginViewTests.test_login_marca_opcao_ativa_do_alternador`

Saída real:

```text
Creating test database for alias 'default'...
.........F......
FAIL: test_login_marca_opcao_ativa_do_alternador
AssertionError: False is not true : Couldn't find 'aria-selected="true" aria-current="page"' in the following response
----------------------------------------------------------------------
Ran 16 tests in 1.634s

FAILED (failures=1)
```

### GREEN

Adicionado `aria-current="page"` ao link ativo “Entrar” em `usuarios/templates/usuarios/login.html`,
sem alterar `usuarios/views.py` nem a lógica de autenticação.

### REFACTOR e testes de caracterização

Como a interface já estava pronta, os demais testes de login são de **caracterização/regressão** —
foram escritos depois da implementação e **não** são apresentados como TDD:

- `test_login_toggle_de_senha_e_acessivel` — `aria-controls`, `aria-label`, `aria-pressed` e ícones;
- `test_login_campos_usam_autocomplete_correto` — `email` e `current-password`;
- `test_login_nao_autentica_apenas_renderiza` — POST não cria sessão autenticada;
- `test_login_alternador_aponta_para_cadastro` — movido de `CadastroViewTests` para
  `LoginViewTests`, apenas para organizar a suíte.

Todos passaram já na primeira execução após o GREEN.

## Página inicial logada — mapa de ocorrências

A rota `/` redirecionava para `/login/`. Agora ela renderiza a tela principal do app em
`usuarios/inicio.html` (`name="inicio"`). A referência “Mapa de ocorrências” foi usada apenas
como inspiração de layout: textos, categorias, endereço e desenho do mapa são originais do
Nossa Rua, sem copiar a tela enviada literalmente. O link “Ver mapa de ocorrências”, no login,
aponta para ela.

**RED** — dois testes escritos antes do novo template:

- `HomeViewTests.test_root_renderiza_mapa_de_ocorrencias`
- `HomeViewTests.test_mapa_tem_filtros_e_ocorrencia_destaque`

Saída real da última rodada RED:

```text
FF
AssertionError: False is not true : Couldn't find 'Vias' in the following response
Ran 2 tests in 0.015s

FAILED (failures=2)
```

**GREEN** — template reescrito com mapa ilustrativo em SVG próprio, busca, filtros
(Vias / Luz / Drenagem / Limpeza), pins de ocorrências, cartão em destaque
(“Iluminação apagada · Rua do Largo, 45”) e navegação inferior (Mapa / Dados / Avisos / Perfil).
Novos tokens de mapa foram adicionados ao `app.css`. Nenhuma lógica de autenticação foi
acrescentada: esta é a **interface** da tela logada, sem bloqueio de acesso.

**REFACTOR** — sem extração de código; a validação final está registrada abaixo.

## Verificação final

Comandos executados a partir de `backend/` (Python 3.11.9, Django 5.2.19, pytest 9.2.0):

```powershell
.\.venv\Scripts\python.exe manage.py test
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\ruff.exe check .
.\.venv\Scripts\python.exe -m pytest
```

O relatório de cobertura é produzido automaticamente pelo pytest porque `backend/pyproject.toml`
define em `[tool.pytest.ini_options]`:

```toml
addopts = "--cov=. --cov-report=term-missing --cov-fail-under=80"
```

Saída consolidada:

```text
python manage.py test    → Ran 20 tests — OK
python manage.py check   → System check identified no issues (0 silenced).
ruff check .             → All checks passed!
pytest                   → 20 passed in 2.33s
TOTAL                    → 255 statements, 2 miss, 99% (99.22%)
```

**Interpretação da cobertura:** os 99,22% (255 instruções, 2 não executadas; no ciclo do cadastro
eram 99,04% — 209 instruções, 2 não executadas) representam a proporção de **instruções de código
executadas** pelos testes no escopo analisado. Esse indicador complementa, mas não substitui, a
verificação dos comportamentos e das regras de negócio. A meta mínima é 80%, definida em
`docs/FRONTEND.md`.

## Observação sobre o histórico no GitHub

Cada ciclo foi registrado em um commit junto com o código final: `5f405b1` (cadastro) e
`2a5672f` (login). Isso é intencional: os ciclos reais aconteceram nesta sessão, mas não foi
possível gerar três commits cronológicos distintos sem reconstruir artificialmente o histórico.
Os ajustes de rigor documental deste texto são registrados em commit posterior. Os trechos acima
são as saídas reais dos comandos executados durante o desenvolvimento.
