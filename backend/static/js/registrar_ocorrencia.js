(function () {
  "use strict";

  const formulario = document.querySelector("form.formulario");
  const botao = document.querySelector("[data-localizacao]");
  const status = document.querySelector("[data-localizacao-status]");
  const campoLatitude = document.getElementById("latitude");
  const campoLongitude = document.getElementById("longitude");

  if (!formulario || !botao || !status || !campoLatitude || !campoLongitude) {
    return;
  }

  const MENSAGENS_ERRO = {
    1: "Permissão negada. Libere a localização no navegador para registrar.",
    2: "Não foi possível descobrir sua posição. Tente novamente.",
    3: "A localização demorou demais. Tente novamente.",
  };

  function onSucesso(posicao) {
    const { latitude, longitude, accuracy } = posicao.coords;
    campoLatitude.value = latitude.toFixed(6);
    campoLongitude.value = longitude.toFixed(6);
    status.textContent =
      "Localização capturada (precisão de " + Math.round(accuracy) + " m).";
    botao.disabled = false;
  }

  function onErro(erro) {
    campoLatitude.value = "";
    campoLongitude.value = "";
    status.textContent =
      MENSAGENS_ERRO[erro.code] || "Não foi possível obter a localização.";
    botao.disabled = false;
  }

  botao.addEventListener("click", function () {
    if (!navigator.geolocation) {
      status.textContent = "Este navegador não oferece localização.";
      return;
    }
    botao.disabled = true;
    status.textContent = "Obtendo sua localização...";
    navigator.geolocation.getCurrentPosition(onSucesso, onErro, {
      enableHighAccuracy: true,
      timeout: 15000,
      maximumAge: 0,
    });
  });

  formulario.addEventListener("submit", function (evento) {
    if (!campoLatitude.value || !campoLongitude.value) {
      evento.preventDefault();
      status.textContent = "Capture sua localização antes de registrar.";
      botao.focus();
    }
  });
})();