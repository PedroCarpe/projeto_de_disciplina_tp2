/*
 * Abas do painel: só alterna o conteúdo visível e o estado ARIA.
 * Não envia requisições, não salva nada e não executa ações administrativas.
 */
(function () {
  "use strict";

  const abas = Array.from(
    document.querySelectorAll('[role="tab"][data-admin-aba]'),
  );

  function ativar(id) {
    abas.forEach(function (aba) {
      const ativa = aba.dataset.adminAba === id;
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

  abas.forEach(function (aba) {
    aba.addEventListener("click", function () {
      ativar(aba.dataset.adminAba);
    });
  });
})();
