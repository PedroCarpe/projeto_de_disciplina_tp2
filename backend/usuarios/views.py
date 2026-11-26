from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


@login_required(login_url="login")
def notificacoes_view(request: HttpRequest) -> HttpResponse:
    """Tela visual de notificações; a integração com o backend vem depois."""
    return render(request, "usuarios/notificacoes.html")
