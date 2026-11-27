from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse, HttpResponseForbidden
from django.shortcuts import render


@login_required(login_url="login")
def painel_view(request: HttpRequest) -> HttpResponse:
    """Painel visual com regra ``is_staff`` provisória até existirem perfis."""
    if not request.user.is_staff:
        return HttpResponseForbidden("Acesso restrito aos administradores.")

    return render(request, "administracao/painel.html")
