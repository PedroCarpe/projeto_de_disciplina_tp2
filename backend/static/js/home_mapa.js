/*
 * Mapa do Nossa Rua. (O componente também se chama `home_mapa` por legado.)
 *
 * Contrato futuro de `ocorrencias` (a view ainda entrega uma lista vazia):
 * {
 *   latitude: number,
 *   longitude: number,
 *   tipo: string,
 *   data: string (ISO 8601 ou dd/mm/aaaa),
 *   status: string,
 *   bairro?: string,
 *   endereco?: string,
 *   categoria?: string,
 *   descricao?: string
 * }
 *
 * Nenhum dado é inventado: enquanto não houver backend, a lista é vazia,
 * os filtros atuam sobre o que vier do servidor e os marcadores não aparecem.
 */
(function () {
  "use strict";

  if (window.NossaRua && window.NossaRua.mapaHomeCarregado) {
    return;
  }

  window.NossaRua = window.NossaRua || {};
  window.NossaRua.mapaHomeCarregado = true;

  function iniciar() {
    const area = document.querySelector("[data-mapa-canvas]");
    const noConfig = document.getElementById("home-mapa-config");
    const botaoLocalizacao = document.querySelector("[data-mapa-localizacao]");
    const status = document.querySelector("[data-mapa-status]");
    const vazio = document.querySelector("[data-mapa-vazio]");
    const vazioTitulo = document.querySelector("[data-mapa-vazio-titulo]");
    const vazioTexto = document.querySelector("[data-mapa-vazio-texto]");
    const campoBusca = document.querySelector("[data-mapa-busca]");
    const painelFiltros = document.getElementById("mapa-filtros");
    const botaoFiltros = document.querySelector("[data-mapa-filtros-toggle]");
    const botaoLimpar = document.querySelector("[data-mapa-limpar]");
    const botaoAplicar = document.querySelector("[data-mapa-aplicar]");
    const contador = document.querySelector("[data-mapa-contador]");
    const detalhe = document.querySelector("[data-mapa-detalhe]");
    const detalheCategoria = document.querySelector("[data-detalhe-categoria]");
    const detalheTipo = document.querySelector("[data-detalhe-tipo]");
    const detalheLocal = document.querySelector("[data-detalhe-local]");
    const detalheData = document.querySelector("[data-detalhe-data]");
    const detalheStatus = document.querySelector("[data-detalhe-status]");
    const detalheDescricao = document.querySelector("[data-detalhe-descricao]");
    const detalheFechar = document.querySelector("[data-detalhe-fechar]");
    const filtros = {
      categoria: document.querySelector('[data-filtro="categoria"]'),
      status: document.querySelector('[data-filtro="status"]'),
      periodo: document.querySelector('[data-filtro="periodo"]'),
    };

    if (!area || !noConfig || typeof window.L === "undefined") {
      if (status) {
        status.textContent = "Mapa indisponível no momento. Tente novamente mais tarde.";
      }
      if (botaoLocalizacao) {
        botaoLocalizacao.disabled = true;
      }
      return;
    }

    let config;
    try {
      config = JSON.parse(noConfig.textContent);
    } catch (erro) {
      if (status) {
        status.textContent = "Não foi possível carregar a configuração do mapa.";
      }
      return;
    }

    const centro = config.centro || {};
    const latitude = Number(centro.lat);
    const longitude = Number(centro.lng);
    const centroInicial = Number.isFinite(latitude) && Number.isFinite(longitude)
      ? [latitude, longitude]
      : [0, 0];
    const semToque = !window.matchMedia || !window.matchMedia("(pointer: coarse)").matches;

    const mapa = window.L.map(area, {
      center: centroInicial,
      zoom: Number(config.zoom) || 13,
      minZoom: Number(config.minZoom) || 4,
      maxZoom: Number(config.maxZoom) || 19,
      zoomControl: true,
      attributionControl: true,
      scrollWheelZoom: semToque,
    });

    /* Sem `referrerPolicy`: o navegador envia o Referer da origem, como pede a
     * política de uso dos tiles do OpenStreetMap. Endpoint recomendado, sem
     * subdomínios ({s}). */
    const provedores = [
      {
        nome: "OpenStreetMap",
        url: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
        opcoes: {
          maxZoom: 19,
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a>',
        },
      },
      {
        nome: "CARTO",
        url: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
        opcoes: {
          maxZoom: 20,
          attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> &copy; <a href="https://carto.com/attributions" target="_blank" rel="noopener noreferrer">CARTO</a>',
        },
      },
    ];

    let indiceProvedor = 0;
    let camadaTiles = null;
    let falhasDeTile = 0;
    let trocandoProvedor = false;

    function trocarProvedor() {
      if (trocandoProvedor || indiceProvedor >= provedores.length - 1) {
        return;
      }
      trocandoProvedor = true;
      indiceProvedor += 1;
      const provedor = provedores[indiceProvedor];

      if (camadaTiles) {
        mapa.removeLayer(camadaTiles);
      }
      camadaTiles = window.L.tileLayer(provedor.url, provedor.opcoes);
      configurarEventosTiles(camadaTiles);
      camadaTiles.addTo(mapa);
      falhasDeTile = 0;
      trocandoProvedor = false;

      if (status) {
        status.textContent =
          "Mapa em provedor alternativo. A localização continua opcional.";
      }
    }

    /* Fallback apenas para falha técnica (tileerror). Um bloqueio por política
     * de uso pode responder 200 com uma imagem de aviso: o Leaflet dispara
     * tileload, não tileerror, e trocar de provedor não resolve a causa — o que
     * resolve é enviar o Referer, como feito acima. */
    function configurarEventosTiles(camada) {
      camada.on("tileload", function () {
        falhasDeTile = 0;
      });
      camada.on("tileerror", function () {
        falhasDeTile += 1;
        if (falhasDeTile >= 3) {
          trocarProvedor();
        }
      });
    }

    function criarCamadaTiles() {
      const provedor = provedores[indiceProvedor];
      camadaTiles = window.L.tileLayer(provedor.url, provedor.opcoes);
      configurarEventosTiles(camadaTiles);
      camadaTiles.addTo(mapa);
    }

    criarCamadaTiles();

    const camadaOcorrencias = window.L.layerGroup().addTo(mapa);
    const camadaLocalizacao = window.L.layerGroup().addTo(mapa);

    /* Ícones são fixos no código: nenhum conteúdo do backend é injetado no HTML
     * do marcador. O texto das ocorrências entra só via textContent. */
    const ICONES = {
      buraco:
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3 2.5 20h19L12 3Z" /><path d="M12 9v5" /><circle cx="12" cy="17" r="0.8" /></svg>',
      iluminacao:
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M9 18h6m-5 3h4M12 2a7 7 0 0 0-4 12.7V18h8v-3.3A7 7 0 0 0 12 2Z" /></svg>',
      lixo:
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M4 7h16M10 4h4M6 7l1 13h10l1-13M10 11v6m4-6v6" /></svg>',
      calcada:
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8h18M3 16h18M8 8v8m8-8v8" /></svg>',
      outros:
        '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="9" /><path d="M12 8v5" /><circle cx="12" cy="16.5" r="0.8" /></svg>',
    };

    const ROTULOS_CATEGORIA = {
      buraco: "Buraco",
      iluminacao: "Iluminação",
      lixo: "Lixo",
      calcada: "Calçada",
      outros: "Outros",
    };

    function normalizarTexto(valor) {
      return String(valor || "")
        .normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase()
        .trim();
    }

    function parsearData(valor) {
      const texto = String(valor || "").trim();
      if (!texto) {
        return null;
      }
      let data = new Date(texto);
      if (Number.isNaN(data.getTime())) {
        const partes = texto.match(/^(\d{2})\/(\d{2})\/(\d{4})$/);
        if (partes) {
          data = new Date(`${partes[3]}-${partes[2]}-${partes[1]}`);
        }
      }
      return Number.isNaN(data.getTime()) ? null : data;
    }

    function formatarData(valor) {
      const data = parsearData(valor);
      return data
        ? new Intl.DateTimeFormat("pt-BR").format(data)
        : String(valor || "").trim();
    }

    function categoriaDe(item) {
      const texto = normalizarTexto(
        [item.categoria, item.tipo].filter(Boolean).join(" ")
      );
      if (/lixo|lixeira|residuo|coleta|entulho/.test(texto)) {
        return "lixo";
      }
      if (/calcad|passeio/.test(texto)) {
        return "calcada";
      }
      if (/luz|lumina|lampada|poste|ilumin/.test(texto)) {
        return "iluminacao";
      }
      if (/buraco|asfalto|via publica|remendo|cratera/.test(texto)) {
        return "buraco";
      }
      return "outros";
    }

    function statusDe(item) {
      const texto = normalizarTexto(item.status);
      if (/andamento|analise|processo/.test(texto)) {
        return "andamento";
      }
      if (/resolv|conclu|finaliz|fechad/.test(texto)) {
        return "resolvido";
      }
      return "aberto";
    }

    function localDe(item) {
      const partes = [item.endereco, item.bairro, item.logradouro, item.local]
        .map(function (valor) {
          return String(valor || "").trim();
        })
        .filter(Boolean);
      return partes.length
        ? partes.join(" — ")
        : `${item.latitude.toFixed(5)}, ${item.longitude.toFixed(5)}`;
    }

    function normalizar(item) {
      if (!item || typeof item !== "object") {
        return null;
      }
      const latitudeItem = Number(item.latitude);
      const longitudeItem = Number(item.longitude);
      if (!Number.isFinite(latitudeItem) || !Number.isFinite(longitudeItem)) {
        return null;
      }
      return {
        latitude: latitudeItem,
        longitude: longitudeItem,
        tipo: String(item.tipo || "Ocorrência"),
        data: String(item.data || ""),
        status: String(item.status || "Aberto"),
        bairro: String(item.bairro || ""),
        endereco: String(item.endereco || item.logradouro || item.local || ""),
        descricao: String(item.descricao || ""),
        categoria: categoriaDe(item),
        statusChave: statusDe(item),
        dataObj: parsearData(item.data),
      };
    }

    function criarIcone(categoria) {
      const chave = Object.prototype.hasOwnProperty.call(ICONES, categoria)
        ? categoria
        : "outros";
      return window.L.divIcon({
        className: "marcador-ocorrencia marcador-ocorrencia--" + chave,
        html:
          '<span class="marcador-ocorrencia__pino"><span class="marcador-ocorrencia__icone">' +
          ICONES[chave] +
          "</span></span>",
        iconSize: [36, 36],
        iconAnchor: [18, 43],
        popupAnchor: [0, -30],
      });
    }

    let marcadorSelecionado = null;

    function limparSelecao() {
      if (marcadorSelecionado) {
        const elemento = marcadorSelecionado.getElement();
        if (elemento) {
          elemento.classList.remove("marcador-ocorrencia--selecionado");
        }
        marcadorSelecionado = null;
      }
    }

    function esconderDetalhes() {
      if (detalhe) {
        detalhe.classList.add("hidden");
      }
      limparSelecao();
    }

    function mostrarDetalhes(item, marcador) {
      if (!detalhe) {
        return;
      }
      limparSelecao();
      if (marcador) {
        marcadorSelecionado = marcador;
        const elemento = marcador.getElement();
        if (elemento) {
          elemento.classList.add("marcador-ocorrencia--selecionado");
        }
      }
      if (detalheCategoria) {
        detalheCategoria.textContent =
          ROTULOS_CATEGORIA[item.categoria] || "Ocorrência";
      }
      if (detalheTipo) {
        detalheTipo.textContent = item.tipo;
      }
      if (detalheLocal) {
        detalheLocal.textContent = localDe(item);
      }
      if (detalheData) {
        detalheData.textContent = item.data ? formatarData(item.data) : "Não informada";
      }
      if (detalheStatus) {
        detalheStatus.textContent = item.status || "Aberto";
      }
      if (detalheDescricao) {
        detalheDescricao.textContent = item.descricao || "Sem descrição informada.";
      }
      detalhe.classList.remove("hidden");
    }

    let ocorrencias = [];

    function aplicarFiltros() {
      const termo = normalizarTexto(campoBusca ? campoBusca.value : "");
      const categoria = filtros.categoria ? filtros.categoria.value : "todas";
      const statusFiltro = filtros.status ? filtros.status.value : "todos";
      const periodo = filtros.periodo ? filtros.periodo.value : "todos";
      const dias = periodo === "todos" ? null : Number(periodo);

      const filtradas = ocorrencias.filter(function (item) {
        if (categoria !== "todas" && item.categoria !== categoria) {
          return false;
        }
        if (statusFiltro !== "todos" && item.statusChave !== statusFiltro) {
          return false;
        }
        if (dias) {
          if (!item.dataObj) {
            return false;
          }
          const limite = Date.now() - dias * 86400000;
          if (
            item.dataObj.getTime() < limite ||
            item.dataObj.getTime() > Date.now() + 86400000
          ) {
            return false;
          }
        }
        if (termo) {
          const texto = normalizarTexto(
            [
              item.bairro,
              item.endereco,
              item.tipo,
              item.descricao,
              item.latitude,
              item.longitude,
            ].join(" ")
          );
          if (!texto.includes(termo)) {
            return false;
          }
        }
        return true;
      });

      camadaOcorrencias.clearLayers();
      filtradas.forEach(function (item) {
        const marcador = window.L.marker([item.latitude, item.longitude], {
          icon: criarIcone(item.categoria),
        });
        marcador.on("click", function () {
          mostrarDetalhes(item, marcador);
        });
        marcador.addTo(camadaOcorrencias);
      });

      esconderDetalhes();

      if (contador) {
        contador.textContent =
          filtradas.length === 1
            ? "1 ocorrência"
            : `${filtradas.length} ocorrências`;
      }
      if (vazio) {
        vazio.hidden = filtradas.length > 0;
        if (!vazio.hidden) {
          if (vazioTitulo) {
            vazioTitulo.textContent = ocorrencias.length
              ? "Nenhuma ocorrência com esses filtros."
              : "Nenhuma ocorrência publicada ainda.";
          }
          if (vazioTexto) {
            vazioTexto.textContent = ocorrencias.length
              ? "Ajuste a busca ou os filtros para ver mais resultados."
              : "Quando houver registros, eles aparecerão aqui com tipo, local, data e status.";
          }
        }
      }
      return filtradas.length;
    }

    function atualizarOcorrencias(lista) {
      ocorrencias = (Array.isArray(lista) ? lista : [])
        .map(normalizar)
        .filter(Boolean);
      return aplicarFiltros();
    }

    atualizarOcorrencias(config.ocorrencias);

    if (campoBusca) {
      campoBusca.addEventListener("input", aplicarFiltros);
    }
    Object.keys(filtros).forEach(function (chave) {
      if (filtros[chave]) {
        filtros[chave].addEventListener("change", aplicarFiltros);
      }
    });
    if (botaoLimpar) {
      botaoLimpar.addEventListener("click", function () {
        if (campoBusca) {
          campoBusca.value = "";
        }
        Object.keys(filtros).forEach(function (chave) {
          if (filtros[chave]) {
            filtros[chave].selectedIndex = 0;
          }
        });
        aplicarFiltros();
      });
    }
    if (botaoAplicar) {
      botaoAplicar.addEventListener("click", function () {
        aplicarFiltros();
        const emCelular =
          !window.matchMedia || window.matchMedia("(max-width: 1023px)").matches;
        if (emCelular && painelFiltros && botaoFiltros) {
          painelFiltros.classList.add("hidden");
          botaoFiltros.setAttribute("aria-expanded", "false");
        }
      });
    }
    if (botaoFiltros && painelFiltros) {
      botaoFiltros.addEventListener("click", function () {
        painelFiltros.classList.toggle("hidden");
        const aberto = !painelFiltros.classList.contains("hidden");
        botaoFiltros.setAttribute("aria-expanded", String(aberto));
      });
    }
    if (detalheFechar) {
      detalheFechar.addEventListener("click", esconderDetalhes);
    }

    if (botaoLocalizacao) {
      botaoLocalizacao.addEventListener("click", function () {
        if (!navigator.geolocation) {
          if (status) {
            status.textContent =
              "Localização indisponível neste dispositivo. O mapa continua funcionando.";
          }
          return;
        }

        if (status) {
          status.textContent = "Solicitando sua localização...";
        }

        function onSucesso(posicao) {
          const lat = posicao.coords.latitude;
          const lng = posicao.coords.longitude;
          mapa.setView([lat, lng], Math.max(mapa.getZoom(), 15));

          const estilos = getComputedStyle(document.documentElement);
          const corLinha = estilos.getPropertyValue("--verde-escuro").trim() || "#1f5240";
          const corPreenchimento = estilos.getPropertyValue("--menta").trim() || "#d5ebdf";

          camadaLocalizacao.clearLayers();
          window.L.circleMarker([lat, lng], {
            radius: 7,
            color: corLinha,
            weight: 3,
            fillColor: corPreenchimento,
            fillOpacity: 1,
          })
            .bindPopup("Sua localização aproximada.")
            .addTo(camadaLocalizacao);

          if (status) {
            status.textContent =
              "Localização encontrada. Você pode navegar pelo mapa normalmente.";
          }
        }

        function onErro() {
          if (status) {
            status.textContent =
              "Não foi possível acessar sua localização. O mapa continua funcionando.";
          }
        }

        navigator.geolocation.getCurrentPosition(onSucesso, onErro, {
          enableHighAccuracy: false,
          timeout: 10000,
          maximumAge: 60000,
        });
      });
    }

    window.addEventListener("resize", function () {
      mapa.invalidateSize();
    });

    window.NossaRua.mapaHome = {
      mapa: mapa,
      atualizarOcorrencias: atualizarOcorrencias,
      aplicarFiltros: aplicarFiltros,
    };
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", iniciar);
  } else {
    iniciar();
  }
})();
