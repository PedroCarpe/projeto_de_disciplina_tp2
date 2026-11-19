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
