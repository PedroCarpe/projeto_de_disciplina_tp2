/*
 * Gráficos da tela de estatísticas.
 * Lê os dados de <script id="estatisticas-dados"> (json_script da view):
 * { total: number, por_tipo: [{tipo, quantidade}], por_data: [{data, quantidade}] }
 */
(function () {
  "use strict";

  var fonte = document.getElementById("estatisticas-dados");
  // Sem Chart.js (CDN fora do ar) a página continua mostrando o total e o aviso.
  if (!fonte || typeof Chart === "undefined") {
    return;
  }

  var dados = JSON.parse(fonte.textContent);
  var verde = "#2f6b55";
  var eixoInteiro = { y: { beginAtZero: true, ticks: { precision: 0 } } };

  new Chart(document.querySelector('[data-grafico="tipo"]'), {
    type: "bar",
    data: {
      labels: dados.por_tipo.map(function (item) { return item.tipo; }),
      datasets: [{
        label: "Ocorrências",
        data: dados.por_tipo.map(function (item) { return item.quantidade; }),
        backgroundColor: verde,
      }],
    },
    options: { scales: eixoInteiro },
  });

  new Chart(document.querySelector('[data-grafico="tempo"]'), {
    type: "line",
    data: {
      labels: dados.por_data.map(function (item) { return item.data; }),
      datasets: [{
        label: "Ocorrências",
        data: dados.por_data.map(function (item) { return item.quantidade; }),
        borderColor: verde,
      }],
    },
    options: { scales: eixoInteiro },
  });
})();
