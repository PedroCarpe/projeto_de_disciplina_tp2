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

## Home — visitante e usuário autenticado

A rota `/` (`name="inicio"`) agora diferencia as experiências com `request.user.is_authenticated`.
Os **dois testes antigos** de `HomeViewTests` (que esperavam pins e cartão de ocorrência) foram
substituídos: a nova especificação não permite dados simulados apresentados como reais. Os
**18 testes já existentes** de login e cadastro não foram alterados.

**Novos testes (9):**

- `HomeVisitanteTests` — 5 testes: template/mensagem, links de Entrar/Cadastrar, Registrar
  levando ao login, estado vazio do mapa sem dados fictícios e ausência de ações restritas.
- `HomeAutenticadoTests` — 4 testes: saudação com o nome, ações e acessos, ausência de links de
  login/cadastro e logout por POST que retorna à Home.

**RED** — comando:

```powershell
.\.venv\Scripts\python.exe manage.py test frontend.test_views.HomeVisitanteTests frontend.test_views.HomeAutenticadoTests
```

Saída real:

```text
FFFFF.FFE
ERROR: test_saida_usa_post_e_encaminha_para_home
django.urls.exceptions.NoReverseMatch: Reverse for 'logout' not found.
AssertionError: False is not true : Template 'includes/home_mapa.html' was not a template used...
AssertionError: False is not true : Couldn't find 'Nenhuma ocorrência publicada ainda.'
AssertionError: 6 != 0 : 'href="#"' unexpectedly found...
Ran 9 tests in 1.546s

FAILED (failures=7, errors=1)
```

Ocorreram 7 falhas e 1 erro; um teste já passava
(`test_autenticado_nao_ve_links_de_login_e_cadastro`).

**GREEN** — `home_view` passa `saudacao` com `first_name` ou username; rota `sair/` com
`LogoutView` (aceita somente POST); `inicio.html` com os dois estados; include
`includes/home_mapa.html` com estado vazio e controle de localização desabilitado; novas classes
em `app.css`; logotipo compartilhado passou a apontar para `/`. Resultado: `Ran 9 tests ... OK`.

**REFACTOR** — apenas CSS: a navegação horizontal do desktop foi trazida para perto do
cabeçalho com `order`. Nenhuma lógica foi extraída. Não há métricas, notificações nem ocorrências
fictícias: recursos sem backend aparecem desabilitados ou como âncoras para seções de estado
vazio.

## Refinamento mobile-first da Home

Sem reconstruir a página, o ciclo seguinte ajustou o que já existia. Foram **8 testes novos**
(3 no visitante, 1 no autenticado e 4 em `HomeCssTests`) e 4 testes existentes da Home foram
ajustados. Os 18 testes de login/cadastro continuaram intactos.

**RED** — comando:

```powershell
.\.venv\Scripts\python.exe manage.py test frontend.test_views.HomeVisitanteTests frontend.test_views.HomeAutenticadoTests frontend.test_views.HomeCssTests
```

Saída real:

```text
F.FF.....FFF..F..
Ran 17 tests in 1.946s

FAILED (failures=7)
```

As falhas cobriram: estrutura compacta sem `Explore sem precisar entrar`, nota de localização
sem botão inexistente, links/ids dos recursos públicos, contagem de controles desabilitados,
modificadores `home--visitante`/`home--autenticado`, ausência de “Notificações” no autenticado
e a proporção `aspect-ratio: 4 / 3` do mapa.

**GREEN** — um único `home__hero` com ramificação interna; título e descrição mais curtos;
`.home--visitante` / `.home--autenticado`; mapa com `aspect-ratio: 4 / 3`, `min-height: 15rem` e
`max-height: 19rem`; remoção do eyebrow, da nota do CTA, dos botões de Notificações/Perfil no
cabeçalho e do botão de localização; `.home__link` com alvo de 44 px; `disabled` nativo nos
controles realmente indisponíveis (1 no visitante, 4 no autenticado, incluindo o CTA).
Resultado: `Ran 17 tests ... OK`.

**REFACTOR** — a primeira suíte completa encontrou `E501` em uma linha de teste; a linha foi
quebrada e a validação foi repetida. Nenhuma lógica de view, rota ou autenticação mudou neste
ciclo.

Lighthouse na Home pública: acessibilidade `1,0` e boas práticas `1,0`. SEO ficou em `0,75`
apenas por ausência de meta description no `base.html` compartilhado, fora do escopo deste
refinamento.

Medições reais no navegador (iframe com CSS local, 844 px de altura): mapa começando em `y=341`
a 360 px e `y=293` a 390 px (antes: `y=440` e `y=414`); altura do mapa de 240/257/287 px em
360/390/430 px; barra inferior colada ao fundo, 5 itens, menor alvo de toque de 44 px, sem
rolagem horizontal e sem `href="#"`. No desktop (1000 px) a navegação é `static`, horizontal e
fica entre o cabeçalho e o hero.

## Mapa interativo com Leaflet e OpenStreetMap

O SVG estático foi substituído por um contêiner Leaflet com tiles do OpenStreetMap. A região
inicial passou a vir de `MAPA_PADRAO` em `setup/settings.py` (São Paulo/SP por padrão) e é
exposta à view por `configuracao_mapa()`, sem nenhum dado de ocorrência. Foram **13 testes novos**
(5 de renderização/configuração no visitante, 1 no autenticado, 1 de CSS e 4 estáticos do JS).

**RED** — comando:

```powershell
.\.venv\Scripts\python.exe manage.py test frontend.test_views.HomeVisitanteTests frontend.test_views.HomeAutenticadoTests frontend.test_views.HomeCssTests frontend.test_views.HomeMapaJsTests
```

Saída real: `.F..FFFF........F..F...E` — `Ran 23 tests in 2.339s`,
`FAILED (failures=7, errors=1)`. O erro era o arquivo `static/js/home_mapa.js`, ainda inexistente.

**GREEN** — `base.html` ganhou os blocos `extra_head`/`extra_scripts`; Leaflet 1.9.4 é carregado
**uma única vez** via unpkg com SRI; `inicio.html` registra o canvas, o status e o JSON de
configuração; `home_mapa.js` inicializa o mapa, adiciona tiles do OSM, controles de zoom, botão
"Minha localização" sob demanda e a interface `atualizarOcorrencias()` para o contrato futuro
(`latitude`, `longitude`, `tipo`, `data`, `status`). Resultado: `Ran 27 tests ... OK`.

**REFACTOR (403 nas tiles)** — durante os testes manuais, o servidor do OSM chegou a devolver
`403 — Access blocked` por volume de requisições. Verifiquei com `curl` que os endpoints respondiam
`200` com qualquer `Referer`, confirmando bloqueio transitório por rate limiting. Acrescentei
`referrerPolicy: "no-referrer"` e um fallback automático para CARTO (`light_all`, também baseado
em dados OSM) após 3 `tileerror`s. Novo RED: `Ran 6 tests ... FAILED (failures=2)`;GREEN:
`Ran 29 tests ... OK`. Um teste corrigiu a asserção para o nome real da API do Leaflet,
`removeLayer`. (O `referrerPolicy: "no-referrer"` foi removido depois; ver a seção “Correção da
política de tiles”.)

Testes manuais no navegador (Chromium, servidor local `runserver`): Leaflet `1.9.4`, 10 tiles
carregadas, 1 CSS e 1 JS, centro inicial `(-23.5505, -46.6333)`, zoom `13`. Zoom `14 → 15 → 14`
e `panBy` alteraram o centro. Localização negada manteve o mapa utilizável; localização simulada
com sucesso centralizou em `(-15.7939, -47.8828)` e desenhou o marcador. Uma ocorrência de teste
gerou o popup `Iluminação — 19/11/2026 · Aberto — (-23.55000, -46.63000)` e ocultou a mensagem
de estado vazio. Ao simular 3 `tileerror`s, o mapa trocou para CARTO preservando marcadores e
atribuição (`© OpenStreetMap © CARTO`); as 10 tiles do provedor alternativo carregaram sem falha.
Lighthouse: acessibilidade `1,0`, boas práticas `1,0`, SEO `0,8` (sem meta description no
`base.html`, fora do escopo).

Medições em 360/390/430 px: mapa de 240/257/287 px de altura, sempre dentro da área, sem
rolagem horizontal, com controles de zoom e atribuição visíveis; 14 tiles carregadas em cada
largura; barra inferior fixa e 5 itens de navegação.

**REFACTOR (alvo de toque)** — a medição inicial mostrou 30 px nos controles de zoom: o
`leaflet.css` é carregado depois do `app.css` e sua regra `.leaflet-touch .leaflet-bar a` tem a
mesma especificidade que a nossa. Novo RED no `HomeCssTests` (`Ran 5 tests ... FAILED (failures=1)`)
e correção com `.home-mapa__area.leaflet-container .leaflet-bar a`, de maior especificidade.
_verificação no navegador: zoom e "Minha localização" com 44 px de altura/largura._

## Simplificação da Home e mapa em página própria

A home deixou de ser uma tela de monitoramento: agora só apresenta o sistema e encaminha para as
áreas disponíveis. O mapa permanece integralmente funcional em `/mapa/`. Foram **10 testes novos**
(6 de `MapaViewTests`, 4 de cartões/ausência de Leaflet na home), vários testes antigos da Home
foram reescritos e 2 testes de CSS de navegação foram substituídos.

**RED** — comando:

```powershell
.\.venv\Scripts\python.exe manage.py test frontend.test_views.HomeVisitanteTests frontend.test_views.HomeAutenticadoTests frontend.test_views.MapaViewTests frontend.test_views.HomeCssTests frontend.test_views.HomeMapaJsTests
```

Saída real: `FEF.....EF..FF..EEEEEEF...F......` — `Ran 33 tests in 2.846s`,
`FAILED (failures=7, errors=8)`. Os erros eram `NoReverseMatch` para o nome `mapa`, ainda
inexistente, e os `reverse()` nos testes que tentavam acessá-lo.

**GREEN** — `urls.py` ganhou `path("mapa/", views.mapa_view, name="mapa")`; `mapa_view` passou a
fornecer `mapa_config`; `usuarios/mapa.html` concentra os blocos Leaflet e reutiliza
`includes/home_mapa.html`; `inicio.html` perdeu o mapa, os acessos rápidos, as seções provisórias
e a navegação inferior, ganhando dois CTAs e três cartões. Resultado: `Ran 33 tests ... OK`.

**REFACTOR** — a suíte completa apontou `F401` (`import re` sem uso); removido, a suíte ficou com
51 testes e `ruff` limpo. Depois, ao medir o navegador, o logotipo compartilhado tinha 40 px de
alvo de toque: novo teste em `HomeCssTests` (com regex restrita ao bloco `.marca`, depois de uma
primeira versão frouxa que passou indevidamente — `Ran 6 tests ... FAILED (failures=1)`) e
`min-height: 2.75rem` aplicado à `.marca`. Resultado final: `Ran 34 tests ... OK` no recorte.

Verificação no navegador: a home tem 0 folhas/scripts Leaflet, 0 canvas de mapa, 3 cartões,
2 CTAs, 2 controles desabilitados e nenhuma barra inferior. Em 360/390/430 px os cartões ficam
empilhados (136 px cada) e o mapa em `/mapa/` mede 246/269/299 px de altura — sem rolagem
horizontal em nenhuma largura. A 1000 px os três cartões ficam na mesma linha. Em `/mapa/`:
Leaflet `1.9.4`, 1 CSS + 1 JS, 10 tiles carregadas, zoom 13, botão de localização e link de
volta ao início, sem erros de console.

## Home elegante com Tailwind (ajuste visual)

Neste ciclo não houve TDD extenso: o professor pediu apenas uma quantidade razoável de testes, não
um teste por detalhe visual. Foram mantidos os testes existentes e acrescentados **2 testes de
guarda** (`TailwindFrontendTests`): um confirma o Tailwind via CDN com a paleta verde/creme e outro
confirma os textos/elementos estruturais da nova home. As duas asserções de título que exigiam uma
frase contígua foram ajustadas para verificar os trechos, já que o realce usa `<span>`.

A home foi refeita a partir do layout enviado pelo usuário: cabeçalho com marca e Entrar/Cadastrar,
eyebrow em pílula, título com “por aqui.” em verde, descrição, dois CTAs, nota “Pequenas atitudes.
Grandes mudanças.”, ilustração vetorial de ruas em verde/creme (`includes/arte_urbana.html`),
seção com kicker/título e três cartões com ícone+seta, e rodapé. O azul da referência foi trocado
pelos tokens do projeto. O Tailwind foi adicionado em `base.html` com `preflight: false`; login,
cadastro, autenticação e `/mapa/` não foram alterados.

Verificação no navegador: Tailwind ativo (`window.tailwind`), hero em duas colunas e cartões em
três colunas a 1000 px; em 360/390/430 px tudo empilha, sem rolagem horizontal e com alvo mínimo
de 44 px. `/login/` mantém o formulário grid e o campo com 40 px. Nenhum erro de console.

A pedido, o mesmo padrão foi aplicado a `/mapa/` sem novo ciclo TDD: `mapa.html` e
`includes/home_mapa.html` ganharam utilitários verdes/creme, mantendo 1 CSS + 1 JS do Leaflet
(`1.9.4`), zoom/pan, 44 px nos controles e nenhuma duplicação. A 1000 px o canvas mede 835×320 px
dentro de um painel arredondado; em 360/390/430 px mede 240/240/266 px de altura, sem rolagem
horizontal, com os controles de zoom em 44 px e 8 tiles carregadas.

## Correção da política de tiles

Revisão do `home_mapa.js` apontou dois problemas no carregamento dos tiles:

1. `referrerPolicy: "no-referrer"` impedia o navegador de enviar o `Referer` nas requisições de
   tiles, contrariando a política de uso do servidor público do OpenStreetMap (que pede para a
   aplicação se identificar quando possível). A configuração foi removida dos dois provedores.
2. O endpoint do OSM usava o formato antigo com subdomínios (`{s}.tile.openstreetmap.org`); foi
   trocado pelo recomendado `https://tile.openstreetmap.org/{z}/{x}/{y}.png`.
3. O fallback para CARTO continua, mas apenas como recurso para **falha técnica** (`tileerror`).
   Um bloqueio por política pode responder `200` com uma imagem de aviso; nesse caso o Leaflet
   dispara `tileload`, não `tileerror`, e trocar de provedor não resolve a causa.
4. `base.html` passou a declarar `<meta name="referrer" content="strict-origin-when-cross-origin">`.
   No navegador embutido usado na verificação, o padrão do Electron enviava `Referer` vazio mesmo
   sem `no-referrer` nas imagens; com a meta explícita, o cabeçalho passou a conter a origem da
   aplicação (`http://127.0.0.1:8024/`). Isso vale para todos os provedores de tiles.

Sem novo ciclo TDD: o teste de guarda do JS foi reescrito para exigir o endpoint sem subdomínios e
a ausência de `referrerPolicy`/`no-referrer`, e o teste do `base.html` passou a cobrir a meta de
referrer. A suíte segue com 54 testes.

Verificação no navegador: 8 tiles carregadas (`200`, `image/png`) apenas em
`tile.openstreetmap.org`, nenhuma com atributo `referrerpolicy`, e `Referer` igual à origem da
página. Nenhum erro de console.

## Interface de exploração do mapa

A pedido, `/mapa/` deixou de ser um componente dentro de um cartão e virou tela de exploração.
Na sequência, a reformulação visual aproximou a página da referência anexada: painel branco de
28 px de raio ocupando 90% da largura útil, sidebar de filtros de 25% separada por linha vertical
suave, barra superior com busca “Buscar região, bairro ou endereço...” e “Minha localização”,
canvas de 520/550 px no desktop e 416 px no celular, cartão flutuante à direita no desktop e
inferior no celular, e legenda abaixo do mapa. O cabeçalho usa exatamente o eyebrow, o título e o
subtítulo pedidos.

Os filtros são “Tipo de ocorrência”, “Período” e “Status”, com “Limpar filtros” e “Aplicar filtros”.
Os pinos `L.divIcon` passaram a distinguir buraco, iluminação, lixo e calçada. O cartão só aparece
para uma ocorrência real selecionada e mostra categoria, título, local, data, status, descrição e
os botões desabilitados “Ver detalhes” e “Acompanhar” — não há rota ou ação fictícia. Nenhum dado,
número, imagem ou estatística foi inventado; `configuracao_mapa()` continua entregando
`"ocorrencias": []` e o estado vazio permanece bem apresentado sobre o mapa.

TDD mantido no mínimo razoável: nenhum teste novo foi criado para detalhe estético. Apenas dois
testes de guarda existentes foram ajustados ao novo texto/altura e um teste da API do JS passou a
verificar os novos seletores e categorias. O teste de tiles continua verificando a ordem OSM →
CARTO, a ausência de `referrerPolicy`/`no-referrer` e a presença de `tileerror`/`tileload`; a
tentativa de usar CARTO Positron como principal foi revertida a pedido. Também foi removida a
mensagem inicial “A localização é opcional; o mapa funciona sem ela.” — o elemento
`data-mapa-status` permanece vazio e sem texto visível, apenas como região `aria-live` para
feedback eventual da geolocalização. Os blocos “403 Access blocked” das capturas eram imagens de
erro do servidor do OSM; com o `Referer` corrigido, a verificação carregou 12 tiles com `200`, sem
mensagem de bloqueio.

Verificação no navegador em viewport desktop de 1440 px: painel 1140×709 px, sidebar 285 px,
coluna do mapa 855 px, canvas 807×550 px com raio de 20 px, busca e botões com 44 px de altura,
sem rolagem horizontal e sem erro de console. Injetando quatro ocorrências apenas na sessão do
navegador pela API pública, a contagem tornou-se “4 ocorrências”, surgiram quatro pinos com classes
por categoria e o cartão mostrou todos os campos, incluindo descrição, com `Ver detalhes` e
`Acompanhar` desabilitados. Filtro por categoria e busca por bairro reduziram para 1 e
“Limpar filtros” restaurou 4; “Aplicar filtros” também fecha o painel no celular. Em 360/390/430 px
o canvas mediu 416 px, os filtros abriram por botão com `aria-expanded`, o cartão apareceu na parte
inferior sem cobrir todo o mapa e não houve rolagem horizontal.

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
python manage.py test    → Ran 55 tests — OK
python manage.py check   → System check identified no issues (0 silenced).
ruff check .             → All checks passed!
pytest                   → 55 passed in 5.58s
TOTAL                    → 479 statements, 2 miss, 99% (99.58%)
```

**Interpretação da cobertura:** os 99,58% (479 instruções, 2 não executadas; no ciclo do cadastro
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
