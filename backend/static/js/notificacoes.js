/*
 * Abas da central de alertas: só alterna o painel visível e o estado ARIA.
 * Não guarda preferências, não envia dados e não executa ações de backend.
 */
(function () {
  "use strict";

  const abas = Array.from(
    document.querySelectorAll('[role="tab"][data-notificacao-aba]'),
  );

  function ativar(id) {
    abas.forEach(function (aba) {
      const ativa = aba.dataset.notificacaoAba === id;
      aba.setAttribute("aria-selected", ativa ? "true" : "false");
      aba.tabIndex = ativa ? 0 : -1;
      aba.classList.toggle("border-verde-escuro", ativa);
      aba.classList.toggle("bg-verde-escuro", ativa);
      aba.classList.toggle("text-white", ativa);
      aba.classList.toggle("hover:bg-[#173e31]", ativa);
      aba.classList.toggle("border-borda", !ativa);
      aba.classList.toggle("bg-white", !ativa);
      aba.classList.toggle("text-verde-escuro", !ativa);
      aba.classList.toggle("hover:bg-salvia/40", !ativa);
      const painel = document.getElementById(aba.getAttribute("aria-controls"));
      if (painel) {
        painel.hidden = !ativa;
      }
    });
  }

  abas.forEach(function (aba, indice) {
    aba.addEventListener("click", function () {
      ativar(aba.dataset.notificacaoAba);
    });

    aba.addEventListener("keydown", function (evento) {
      let proximo = null;

      switch (evento.key) {
        case "ArrowRight":
          proximo = (indice + 1) % abas.length;
          break;
        case "ArrowLeft":
          proximo = (indice - 1 + abas.length) % abas.length;
          break;
        case "Home":
          proximo = 0;
          break;
        case "End":
          proximo = abas.length - 1;
          break;
        default:
          return;
      }

      evento.preventDefault();
      abas[proximo].focus();
      ativar(abas[proximo].dataset.notificacaoAba);
    });
  });
})();
