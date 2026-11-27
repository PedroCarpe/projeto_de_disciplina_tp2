# Design system do frontend — Nossa Rua

Nome do produto em todas as telas: **Nossa Rua**.

Fonte única: `backend/static/css/app.css`. `base.html` apenas carrega esse CSS.
Todas as telas devem reutilizar tokens e classes — não crie cores, raios ou sombras locais.

## Paleta oficial

Linguagem visual alinhada à referência enviada, com o nome **Nossa Rua**.

| Variável | Hex | Uso |
| --- | --- | --- |
| `--creme` | `#FBF8F3` | Fundo das telas |
| `--tinta` | `#26323B` | Texto principal |
| `--verde` | `#2F6B55` | Ação, links e logotipo |
| `--verde-escuro` | `#1F5240` | Botão principal |
| `--verde-escuro-hover` | `#173E31` | Hover do botão principal |
| `--menta` | `#D5EBDF` | Resolvido / acentos suaves |
| `--lavanda` | `#E1DCF5` | Registrada |
| `--pessego` | `#FFDFCF` | Destaque e ponto do logotipo |
| `--ceu` | `#D6E8F5` | Em andamento |
| `--manteiga` | `#FBF0C8` | Em análise |
| `--branco` | `#FFFFFF` | Painéis e campos |

Aliases mantidos: `--verde-creme`, `--branco-quente`, `--salvia`. Derivados: `--texto-secundario` (`#5E6B73`), `--verde-cinza`, `--borda` (`#EDE6DB`), `--linha`, `--placeholder`. Validação: `--erro` (`#9B3B2E`) e `--erro-suave` (`#FBE9E4`).

Fonte: **Nunito** (400/600/700/800). Raios: campos `18px`, botões `16px`, cartões `22px`.

## Papéis semânticos

Use sempre: `--cor-fundo`, `--cor-painel`, `--cor-texto`, `--cor-texto-muto`, `--cor-borda`, `--cor-destaque`, `--cor-link`, `--cor-foco`, `--cor-placeholder`.

## Logotipo

Include reutilizável: `{% include "includes/logo.html" %}`.

Composição: quadrado verde arredondado com pin branco, centro verde e ponto pêssego + `Nossa Rua` em **Nunito ExtraBold (800)**, cor `#2F6B55`, com o ponto final em `#FFDFCF`. Sem sombra, 3D ou gradiente.

| Classe | Função |
| --- | --- |
| `.marca` | Contêiner alinhado horizontalmente |
| `.marca__icone` | Quadrado verde com pin |
| `.marca__pin`, `.marca__centro`, `.marca__brilho` | Partes do pin |
| `.marca__nome` | Texto da marca |
| `.marca__ponto` | Ponto final em pêssego |

## Componentes compartilhados

| Grupo | Classes |
| --- | --- |
| Estrutura | `.autenticacao`, `.apresentacao`, `.apresentacao__conteudo`, `.acesso`, `.acesso__conteudo` |
| Apresentação | `.apresentacao__frases`, `.apresentacao__frase`, `.apresentacao__frase-secundaria`, `.linha-mapa` |
| Texto de acesso | `.etiqueta`, `.etiqueta__icone`, `.acesso__titulo`, `.acesso__subtitulo`, `.acesso__visitante` |
| Alternador | `.alternador`, `.alternador__opcao`, `.alternador__opcao--ativa` |
| Formulário | `.formulario`, `.campo`, `.campo__etiqueta`, `.campo__grupo`, `.campo__icone`, `.campo__controle`, `.campo__acao` |
| Validação | `.aviso-erro`, `.aviso-sucesso`, `.campo__grupo--invalido`, `.campo__erro` |
| Botão e link | `.ligacao`, `.botao`, `.botao--primario`, `.botao--secundario`, `.botao__seta` |
| Home | `.home`, `.home--visitante`, `.home--autenticado`, `.home__link`, `.home__sair`, `.home__botao-pequeno`, `.home__saudacao`, `.home__titulo`, `.home__descricao`, `.home__cta`, `.home__cta--secundario`, `.home__eyebrow`, `.home__cartoes`, `.home__cartoes-titulo`, `.hero`, `.hero-copy`, `.hero-footnote`, `.explore`, `.section-heading`, `.section-kicker`, `.site-shell` |
| Cartões da Home | `.home-cartoes`, `.home-cartao`, `.feature-icon`, `.feature-copy`, `.feature-title`, `.feature-description`, `.feature-arrow` |
| Ilustração da Home | `.urban-art`, `.street-map`, `.art-note`, `.note-icon`, `.note-dot`, `.art-caption` (`includes/arte_urbana.html`) |
| Página do mapa | `.pagina-mapa`, `.site-shell`, `.home-mapa`, `.home-mapa__area` (`.leaflet-container`), `.home-mapa__vazio`, `.marcador-ocorrencia`, `.marcador-ocorrencia__pino`, `.marcador-ocorrencia__icone`, `.marcador-ocorrencia--buraco/--iluminacao/--lixo/--calcada/--outros` |
| Exploração | `[data-mapa-busca]`, `[data-mapa-filtros-toggle]`, `[data-mapa-filtros]`, `[data-filtro="categoria/periodo/status"]`, `[data-mapa-limpar]`, `[data-mapa-aplicar]`, `[data-mapa-contador]`, `[data-mapa-detalhe]`, `[data-detalhe-categoria/tipo/local/data/status/descricao]`, `[data-detalhe-fechar]`, `[data-detalhe-acompanhar]`, `[data-mapa-localizacao]` |
| Leaflet (temas) | `.leaflet-bar`, `.leaflet-control-attribution`, `.leaflet-control-zoom-in`, `.leaflet-control-zoom-out` — os alvos de toque são sobrescritos em `.home-mapa__area.leaflet-container .leaflet-bar a` para 44 px |

## Regras

1. Estenda `base.html` e use `{% block content %}`.
2. Reutilize as classes acima antes de criar novas.
3. Cores e fontes vivem em dois lugares: `--tokens` em `app.css` e o `tailwind.config` em `base.html`. Evite hexadecimal avulso nos templates; a ilustração vetorial é a exceção controlada.
4. Mobile primeiro: uma coluna; a partir de `48rem`, apresentação à esquerda e formulário à direita.
5. Campos, botões e links continuam sendo HTML real e acessível.
6. Telas de autenticação: `/login/` e `/cadastro/`. O cadastro usa os mesmos componentes do login e exibe erros via `.aviso-erro` e `.campo__erro` (servidor e JavaScript), e sucesso via `.aviso-sucesso`.
7. Cadastro: usa o `User` padrão do Django com `username = e-mail`; e-mail é único (comparação sem diferenciar maiúsculas) e a senha é salva com hash.
8. Home em `/` (`name="inicio"`): apresentação e navegação, sem mapa e sem barra inferior. `home_view` usa `request.user.is_authenticated`. Visitante vê Entrar/Cadastrar, “Criar conta para participar” e “Explorar mapa”; autenticado vê saudação, “Sua cidade, mais bem cuidada.”, o CTA “Registrar ocorrência” desabilitado e logout por POST em `/sair/`. O logotipo compartilhado aponta para `/`.
9. Mapa em `/mapa/` (`name="mapa"`), público e com Leaflet 1.9.4 + tiles do OpenStreetMap (endpoint sem subdomínios, sem `referrerPolicy` para enviar o `Referer`; fallback para CARTO após 3 `tileerror`s, só falhas técnicas) carregados uma única vez com SRI. O include `includes/home_mapa.html` concentra painel de 28 px, sidebar de filtros (25%), barra de busca, canvas, legenda e cartão de detalhes; a largura útil do painel é 90%. O canvas tem 416 px no celular, 520 px a partir de `lg` e 550 px em `xl`. Região inicial em `MAPA_PADRAO` (`setup/settings.py`); centro, zoom e limites vêm da view. “Minha localização” fica na barra superior e pede permissão só no clique; se negada, o mapa continua funcionando. No celular os filtros ficam atrás de um botão e os detalhes aparecem em cartão inferior. Categorias reais dos marcadores: buraco, iluminação, lixo, calçada e outros. Busca, filtros, contagem e marcadores atuam apenas sobre os dados enviados pelo backend — sem dados simulados. Sem gráficos ou estatísticas nesta página.
10. A Home é mobile-first e usa Tailwind via CDN com a paleta do projeto: cabeçalho com marca e Entrar/Cadastrar, hero com eyebrow em pílula, título com palavra em verde, dois CTAs, rodapé de texto e uma ilustração vetorial de ruas em verde/creme. Abaixo, a seção “Explore a plataforma” tem kicker, título e três cartões com ícone, descrição e seta. No celular tudo empilha; a partir de `md` o hero vira duas colunas e os cartões ficam em uma linha. Não há barra inferior. Alvos de toque medem ao menos 44 px, inclusive a marca compartilhada.
11. Mapa, Estatísticas, Alertas e cadastro levam a rotas reais; não há `href="#"` nem ação simulada. Recursos ainda sem backend são explícitos: no autenticado, o CTA “Registrar ocorrência” usa `disabled` nativo.

## Componentes do painel administrativo

A página única `/administracao/` segue as mesmas tokens e componentes; **nenhum CSS novo**
foi criado. Ela estende `base.html`, reaproveita `.site-shell`, `.home__link`, `.home__saudacao`,
`.botao`, `.botao--primario`, `.home__eyebrow`, o include da marca e os utilitários Tailwind
já declarados em `base.html`.

| Grupo | Classes/atributos |
|---|---|
| Estrutura do painel | `.site-shell`, `.hero`, `.hero-copy`, `.home__eyebrow`, `.home__saudacao` |
| Navegação das abas | `[role="tablist"]`, `[role="tab"]`, `[data-admin-aba]`, `aria-selected`, `aria-controls`, `tabindex` |
| Painéis | `[role="tabpanel"]`, `[data-admin-painel]`, `aria-labelledby`, `hidden` |
| Estados vazios | Cartões com `border-borda`, `bg-[#fdfcf9]`, `rounded-[1.25rem]` e ícone em `bg-salvia/70 text-verde` |
| Tabelas | `min-w-[36rem]` / `min-w-[32rem]` dentro de `overflow-x-auto`, cabeçalho `bg-[#fdfcf9]` |
| Ações indisponíveis | `disabled` nativo + `aria-disabled="true"`, sem `title` com detalhes internos |
| Script | `static/js/admin.js`, carregado com `defer`, alternância das abas apenas por clique |

Os status das ocorrências são textos — `Pendente`, `Em andamento`, `Resolvida` — apresentados
em pílulas `bg-salvia/40` com `text-verde-escuro`. Não foram introduzidas novas cores, raios,
sombras ou fontes. Valores ausentes em relatórios são exibidos como `—` com a legenda
`Sem dados`, nunca como zero ou número inventado. As pendências de integração ficam registradas
apenas nesta documentação, nunca na interface.

Regras adicionais:

12. O painel administrativo é protegido por `is_staff` apenas provisoriamente; a regra
   definitiva deve vir do backend quando existirem perfis/permissões. Usuário comum recebe
   403 e visitante é encaminhado ao login existente com `next`.
13. `/admin/` permanece como Django Admin nativo. `/administracao/` é uma tela visual
   separada, com abas internas e estados vazios; não substitui nem modifica o admin.
14. Toda ação que ainda não tem backend usa `disabled` nativo. Não há link `href="#"`,
   formulário de configuração, persistência nem dado simulado no painel.
15. A navegação reusa classes existentes: o botão de administrador na home usa
   `.botao--secundario.home__botao-pequeno` e aparece só com `user.is_staff`; **Sair** mantém o
   POST real com ícone, e **Voltar ao início** no painel usa `.home__link`.
16. As quatro abas do painel usam `role="tablist"`/`role="tab"`/`role="tabpanel"`,
   `aria-controls`, `aria-labelledby`, `aria-selected`, `tabindex` e `hidden`. `admin.js` alterna
   o estado apenas por clique e troca as classes visuais junto com `aria-selected`: a aba ativa
   fica com `bg-verde-escuro`/`text-white` e as inativas com `bg-white`/`text-verde-escuro`.
   Não há animação, storage, `fetch`, submit ou requisição ao backend.

## Componentes da central de notificações

A página única `/notificacoes/` segue as mesmas tokens e componentes da home e do painel:
estende `base.html`, reaproveita `.site-shell`, `.home__link`, `.home__saudacao`, `.botao`, o
include da marca e os utilitários Tailwind já declarados. **Nenhum CSS novo** foi criado para
ela; a limpeza feita no login apenas removeu a regra `.acesso__visitante`, que não é mais usada.

17. O acesso usa `@login_required(login_url="login")`: visitante é encaminhado ao login com
   `next`, e qualquer usuário autenticado entra, sem exigir `is_staff`. O cabeçalho traz
   “Voltar ao início”, o badge **Alertas** com `aria-current="page"` e o POST real de logout.
   Os cartões **Alertas** e **Estatísticas** da home são links reais para suas rotas.
18. As três abas (Notificações, Favoritos e Preferências) usam `role="tablist"`/`role="tab"`/
   `role="tabpanel"`, `aria-controls`, `aria-labelledby`, `aria-selected`, `tabindex` e `hidden`.
   `notificacoes.js` alterna o estado por clique e pelas teclas ArrowRight, ArrowLeft, Home e
   End, trocando as classes visuais junto com `aria-selected`: a aba ativa fica com
   `bg-verde-escuro`/`text-white` e as inativas com `bg-white`/`text-verde-escuro`. Não há
   animação, storage, `fetch` ou submit.
19. Os painéis reaproveitam o cartão de estado vazio com ícone em `bg-salvia/70`, textos em
   `#67756c` e o botão desabilitado. Os textos são neutros e não citam integração, backend ou
   etapas de desenvolvimento; as pendências ficam apenas nesta documentação. Apenas o link
   **Explorar mapa** executa navegação real.
