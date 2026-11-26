# Frontend — Métodos e Ferramentas

> Proposta do time de frontend. Pode mudar conforme o grupo decidir.

## 1. Arquitetura

**Server-Side Rendering com Django Templates + "ilhas" de JavaScript.**

- Cada tela é uma view do Django que renderiza um template HTML.
- JavaScript só entra onde há real necessidade: **mapa**, **gráficos de estatísticas** e **captura de GPS**.
- Não há API separada entre back e front. Os dados chegam ao JavaScript pelo filtro nativo `json_script` do Django (já protegido contra XSS):

```django
{{ ocorrencias|json_script:"dados-ocorrencias" }}
<script>
  const ocorrencias = JSON.parse(
    document.getElementById("dados-ocorrencias").textContent
  );
</script>
```

- Se algum filtro precisar atualizar sem recarregar a página, usamos uma view simples com `JsonResponse` (sem Django REST Framework).

## 2. Bibliotecas

Todas carregadas por CDN: **sem Node, sem npm e sem etapa de build**.

| Biblioteca | Uso | Licença |
|---|---|---|
| [Django Templates](https://docs.djangoproject.com/en/5.2/topics/templates/) | Renderização das telas | BSD-3 |
| [Tailwind CSS](https://tailwindcss.com/) | Estilo e layout responsivo | MIT |
| [Leaflet](https://leafletjs.com/) | Mapa de ocorrências | BSD-2 |
| [OpenStreetMap](https://www.openstreetmap.org/) | Imagens (tiles) do mapa | ODbL (exige atribuição no mapa) |
| [Chart.js](https://www.chartjs.org/) | Gráficos de estatísticas | MIT |
| [Vue 3](https://vuejs.org/) (opcional, via CDN) | Só em ilhas que precisarem de reatividade | MIT |

APIs nativas do navegador:

- `navigator.geolocation`: posição GPS ao registrar uma ocorrência.

## 3. Estrutura de pastas

```text
backend/
├── templates/
│   ├── base.html            # layout comum (menu, Tailwind, blocos)
│   └── <app>/<tela>.html    # uma pasta por app do Django
└── static/
    ├── js/
    │   ├── mapa.js          # ilha do mapa (Leaflet)
    │   ├── estatisticas.js  # ilha dos gráficos (Chart.js)
    │   └── gps.js           # captura de localização
    └── css/
        └── app.css          # só o que o Tailwind não cobrir
```

Regras:

- Sem `<script>` com lógica dentro do HTML; a lógica fica em `static/js/`. O template só entrega os dados (`json_script`).
- Todo template estende `base.html`.

## 4. Telas

| Tela | Ilha JS | Observação |
|---|---|---|
| Registrar ocorrência | GPS | Tipo escolhido de uma lista definida pelo admin |
| Mapa de ocorrências | Leaflet | Marcadores com tipo e data |
| Detalhe da ocorrência | — | Botão "acompanhar" |
| Estatísticas | Chart.js | Por região e evolução no tempo |
| Minhas notificações | — | Lista dentro do site, com contador no menu |
| Alertas por área/tipo | Leaflet (opcional) | Escolher área e tipos de ocorrência |
| Administração e relatório | — | Base no Django Admin |

## 5. Responsividade (mobile-first)

- O sistema deve rodar no celular. Cada tela é desenhada primeiro para a largura do celular e depois expandida com os prefixos do Tailwind (`md:`, `lg:`).
- Teste no computador: DevTools (`F12`) → modo dispositivo (`Ctrl+Shift+M`). Também dá para simular a localização em *Sensors*.
- **GPS no celular só funciona em HTTPS ou `localhost`.** Para testar em um celular de verdade, usar um túnel HTTPS (ex.: ngrok).

## 6. Testes (TDD)

- **Framework:** Pytest + `pytest-django` (o mesmo do backend).
- Cada tela tem testes **antes** da implementação, verificando:
  - status da resposta (200, redirecionamento para login, 403/404);
  - template usado (`assertTemplateUsed`);
  - dados enviados ao template (contexto e `json_script`);
  - conteúdo essencial presente no HTML.
- **Cobertura:** `pytest-cov`, meta ≥ 80%. Como as telas são views em Python, elas entram na cobertura.
- O JavaScript fica pequeno e sem regra de negócio; cálculos (estatísticas, filtros) são feitos no Python, onde são testados.

## 7. Padrão de código

| Linguagem | Padrão | Verificador |
|---|---|---|
| Python (views) | PEP 8 | Ruff (já configurado) |
| Templates HTML | Padrão Django | djLint (GPL-3.0, instala via `pip`) — *a confirmar* |
| JavaScript | [Google JavaScript Style Guide](https://google.github.io/styleguide/jsguide.html) | ESLint exige Node — *a decidir com o grupo* |

## 8. Ferramentas de desenvolvimento

- **Editor:** VS Code, com as extensões Python, Ruff, Django e Tailwind CSS IntelliSense.
- **Versionamento:** Git + GitHub, uma branch por funcionalidade (`feature/<nome>`) e Pull Request para a `main`.
- **Gestão:** quadro Scrum/Kanban do grupo, com uma tarefa por tela.
- **Teste no celular:** ngrok (opcional).

## 9. Decisões pendentes

- [ ] Verificador de padrão para templates (djLint?) e para JavaScript.
- [ ] Usar Vue via CDN em alguma ilha ou ficar só com JavaScript puro.
- [ ] Banco: SQLite com latitude/longitude ou PostGIS (afeta como o mapa recebe os dados).

## 10. Estado atual das integrações

**Home (`/`) é de apresentação e navegação.** Segue o layout de referência (cabeçalho, hero com
ilustração vetorial, seção “Explore a plataforma” e rodapé), mas com a identidade verde/creme do
projeto — nenhum azul foi adotado. Dois CTAs (“Criar conta para participar” e “Explorar mapa”) e
três cartões (Mapa, Estatísticas, Alertas). O mapa, os links provisórios e a barra inferior foram
removidos da home; o componente do mapa foi preservado e reutilizado na página própria.

**Tailwind CSS via CDN** é carregado uma vez em `base.html` com `corePlugins: { preflight: false }`
para não alterar as telas de login/cadastro, que continuam em `app.css`. O `tailwind.config`
declara `creme`, `tinta`, `verde`, `verde-escuro`, `salvia`, `borda`, a fonte Nunito e os raios
`botao`/`cartao`. A home, a página `/mapa/` e os includes `arte_urbana.html` e `home_mapa.html`
usam utilitários (`grid`, `md:grid-cols-3`, `gap-*`, `rounded-*`, `bg-salvia/70`, `text-verde`,
etc.); `app.css` mantém tokens, componentes compartilhados, reset e os ajustes específicos do
Leaflet. A ilustração é SVG inline com a paleta do projeto — sem imagem externa e sem dados
simulados.

**Mapa em `/mapa/` (`name="mapa"`), público para visitantes e autenticados.** A página segue a
composição de referência: cabeçalho com marca e “Voltar ao início”, eyebrow “MAPA DE OCORRÊNCIAS”,
título “Explore a cidade.” (com “cidade.” em verde) e subtítulo “Navegue pelo mapa e veja as
ocorrências registradas na sua região.”. Abaixo, um painel branco de cantos de 28 px ocupa 90% da
largura útil e se divide em sidebar de filtros (25%) e área do mapa (75%), separadas por linha
vertical suave; no desktop o painel mediu 1140 px, a sidebar 285 px e o mapa 855 px.

A sidebar traz “Filtros”, “Limpar filtros”, os seletores “Tipo de ocorrência”, “Período” e
“Status” e o botão verde-escuro “Aplicar filtros”. Acima do mapa ficam a busca “Buscar região,
bairro ou endereço...” e o botão “Minha localização”. O canvas tem 520 px no desktop a partir de
`lg` e 550 px em telas grandes (`xl`), com cantos de 20 px; no celular mede 416 px. Marcadores
`L.divIcon` usam ícones verdes por categoria (buracos, iluminação, lixo e calçadas) e, ao selecionar
um marcador real, abre-se um cartão à direita no desktop ou inferior no celular com categoria,
título, local, data, status, descrição e os botões desabilitados “Ver detalhes” e “Acompanhar”.
A legenda das categorias fica abaixo do mapa. Não há gráficos nem estatísticas nesta página.

`mapa.html` carrega
Leaflet `1.9.4` via unpkg com SRI uma única vez (`{% block extra_head %}` /
`{% block extra_scripts %}`) e `static/js/home_mapa.js` inicializa `#home-mapa-canvas`. A região
inicial vem de `MAPA_PADRAO` em `setup/settings.py` (`lat`, `lng`, `zoom`) e é passada como JSON
pela view — sem depender de GPS. Zoom, arrasto e atribuição são reais. Os tiles usam o endpoint
recomendado `tile.openstreetmap.org` (sem subdomínios) como provedor principal e **não** definem
`referrerPolicy`, para que o navegador envie o `Referer` exigido pela política de uso do
OpenStreetMap — `base.html` também declara
`<meta name="referrer" content="strict-origin-when-cross-origin">` para deixar isso explícito. O
CARTO (`light_all`) voltou a atuar apenas em falha técnica (`tileerror`): um bloqueio por política
que responde `200` com imagem de aviso dispara `tileload`, não `tileerror`, e não se resolve trocando
de provedor.

O botão “Minha localização” chama `getCurrentPosition` somente após o clique; permissão negada
ou dispositivo sem GPS apenas atualiza o status, sem interromper o mapa. A mensagem “Nenhuma
ocorrência publicada ainda.” aparece discreta sobre o mapa e não bloqueia a interação; quando
existem dados mas os filtros não retornam nada, o texto muda para “Nenhuma ocorrência com esses
filtros.”.

Não existe ainda modelo, API ou endpoint de ocorrências, estatísticas, alertas ou perfil — e
nenhum foi criado. `configuracao_mapa()` entrega `"ocorrencias": []` e o JS expõe
`window.NossaRua.mapaHome.atualizarOcorrencias(lista)` e `aplicarFiltros()`, prontas para o
contrato futuro com `latitude`, `longitude`, `tipo`, `data` e `status` (mais `bairro`, `endereço`,
`categoria` e `descrição` opcionais). Busca, filtros, contagem e cartão de detalhes funcionam sobre
essa lista; nenhum dado é inventado para preencher o mapa.
Chart.js continua apenas proposta. Os cartões Estatísticas e Alertas usam `disabled` nativo e,
no autenticado, o CTA “Registrar ocorrência” também. Rotas futuras como `estatisticas` e
`alertas` só devem ser referenciadas por `{% url %}` depois de existirem no `urls.py`, para
evitar `NoReverseMatch`. O logout, por outro lado, já é real: usa `LogoutView` por POST em
`/sair/` e retorna para `/`.

## Central de notificações

A página `/notificacoes/` (`name="notificacoes"`) vive no app `usuarios` e protege o acesso com
`@login_required(login_url="login")`: visitante é encaminhado ao login com `next`; qualquer
usuário autenticado entra, sem exigir `is_staff`. A view `notificacoes_view` está em
`usuarios/views.py`, a rota foi registrada no `frontend/urls.py` existente e a view apenas faz
`render` de `usuarios/notificacoes.html`, sem contexto extra, modelo ou persistência.

A tela reúne três abas na mesma URL, alternadas por `static/js/notificacoes.js` (JavaScript
puro, com ARIA e navegação por teclado):

- **Notificações**: estado vazio “Você ainda não recebeu nenhuma notificação” e explicação de
  que as atualizações das ocorrências acompanhadas aparecerão nessa área;
- **Favoritos**: estado vazio “Nenhuma ocorrência favoritada”, explicação do acompanhamento e
  link real para o mapa existente (`{% url 'mapa' %}`);
- **Preferências**: estado vazio enquanto não há integração, sem formulário, com o botão
  **Salvar preferências** desabilitado.

O cartão **Alertas** da home deixou de ser desabilitado e passou a ser um link real para a nova
rota. O cartão **Estatísticas** continua desabilitado. Nenhum favorito, notificação, tipo de
ocorrência, API, `fetch`, `localStorage` ou dado fictício foi criado: o conteúdo das três abas é
somente o estado vazio aguardando o backend.

Nenhum modelo, migration, banco, autenticação, painel administrativo, mapa ou home foi reformulado.
As alterações fora do app `usuarios` se resumem à rota em `frontend/urls.py`, ao cartão **Alertas**
em `usuarios/templates/usuarios/inicio.html` e ao JavaScript em `static/js/notificacoes.js`.
A primeira versão desta tela chegou a usar um app `notificacoes` independente; a organização foi
simplificada a pedido e o app foi removido, sem deixar registro em `INSTALLED_APPS` ou `setup/urls.py`.
