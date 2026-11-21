from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def login_view(request: HttpRequest) -> HttpResponse:
    """Renderiza a tela de login (apresentação, sem autenticação ainda)."""
    return render(request, "usuarios/login.html")
