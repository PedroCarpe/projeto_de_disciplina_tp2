from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from .forms import OcorrenciaForm


@login_required
def registrar_ocorrencia_view(request: HttpRequest) -> HttpResponse:
    """Exibe o formulário ou salva uma ocorrência enviada por POST."""
    if request.method == "POST":
        formulario = OcorrenciaForm(request.POST)
        if formulario.is_valid():
            formulario.save(request.user)
            messages.success(request, "Ocorrência registrada com sucesso.")
            return redirect("registrar_ocorrencia")
    else:
        formulario = OcorrenciaForm()

    return render(
        request,
        "ocorrencias/registrar_ocorrencia.html",
        {
            "formulario": formulario,
            "tipos": formulario.fields["tipo"].choices,
        },
    )
