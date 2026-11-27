from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from .models import Ocorrencia


@login_required
def registrar_ocorrencia_view(request: HttpRequest) -> HttpResponse:
    """Renderiza o formulário de registro de ocorrência."""
    return render(
        request,
        "ocorrencias/registrar_ocorrencia.html",
        {"tipos": Ocorrencia.Tipo.choices},
    )
