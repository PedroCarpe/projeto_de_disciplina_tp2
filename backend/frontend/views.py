from django.conf import settings
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

MAPA_PADRAO_FALLBACK = {"lat": -23.5505, "lng": -46.6333, "zoom": 13}


def configuracao_mapa() -> dict:
    """Devolve a configuração pública do mapa, sem dados de ocorrências."""
    padrao = getattr(settings, "MAPA_PADRAO", None) or MAPA_PADRAO_FALLBACK
    return {
        "centro": {
            "lat": float(padrao.get("lat", MAPA_PADRAO_FALLBACK["lat"])),
            "lng": float(padrao.get("lng", MAPA_PADRAO_FALLBACK["lng"])),
        },
        "zoom": int(padrao.get("zoom", MAPA_PADRAO_FALLBACK["zoom"])),
        "minZoom": 4,
        "maxZoom": 19,
        "ocorrencias": [],
    }


def home_view(request: HttpRequest) -> HttpResponse:
    """Renderiza a home, personalizada para usuários autenticados."""
    saudacao = ""
    if request.user.is_authenticated:
        nome = request.user.first_name.strip() or request.user.get_username()
        saudacao = f"Olá, {nome}"
    return render(request, "usuarios/inicio.html", {"saudacao": saudacao})


def mapa_view(request: HttpRequest) -> HttpResponse:
    """Renderiza o mapa interativo em página própria, pública para visitantes."""
    return render(request, "usuarios/mapa.html", {"mapa_config": configuracao_mapa()})


def login_view(request: HttpRequest) -> HttpResponse:
    """Autentica o usuário e renderiza a tela em caso de falha."""
    if request.method != "POST":
        return render(request, "usuarios/login.html")

    email = (request.POST.get("email") or "").strip()
    senha = request.POST.get("senha") or ""
    usuario = authenticate(request, username=email, password=senha)

    if usuario is not None:
        login(request, usuario)
        return redirect("inicio")

    return render(
        request,
        "usuarios/login.html",
        {"erro": "E-mail ou senha inválidos."},
    )


def validar_cadastro(
    nome: str, email: str, senha: str, confirmacao: str
) -> dict[str, str]:
    """Valida os dados do cadastro e devolve mensagens por campo."""
    erros: dict[str, str] = {}

    if not nome:
        erros["nome"] = "Informe seu nome completo."

    if not email:
        erros["email"] = "Informe seu e-mail."
    else:
        try:
            validate_email(email)
        except ValidationError:
            erros["email"] = "Informe um e-mail válido."
        else:
            if User.objects.filter(email__iexact=email).exists():
                erros["email"] = "Este e-mail já está cadastrado."

    if not senha:
        erros["senha"] = "Crie uma senha."
    elif len(senha) < 8:
        erros["senha"] = "A senha deve ter pelo menos 8 caracteres."

    if not confirmacao:
        erros["confirmacao_senha"] = "Confirme sua senha."
    elif senha and confirmacao != senha:
        erros["confirmacao_senha"] = "As senhas não coincidem."

    return erros


def criar_usuario(nome: str, email: str, senha: str) -> None:
    """Cria um usuário com o e-mail como username e a senha com hash."""
    partes = nome.split(maxsplit=1)
    User.objects.create_user(
        username=email,
        email=email,
        password=senha,
        first_name=partes[0],
        last_name=partes[1] if len(partes) > 1 else "",
    )


def cadastro_view(request: HttpRequest) -> HttpResponse:
    """Renderiza o cadastro e cria o usuário quando os dados são válidos."""
    if request.method != "POST":
        return render(request, "usuarios/cadastro.html")

    nome = (request.POST.get("nome") or "").strip()
    email = (request.POST.get("email") or "").strip()
    senha = request.POST.get("senha") or ""
    confirmacao = request.POST.get("confirmacao_senha") or ""

    erros = validar_cadastro(nome, email, senha, confirmacao)
    sucesso = ""

    if not erros:
        criar_usuario(nome, email, senha)
        sucesso = "Conta criada com sucesso. Acesse com seu e-mail e senha."
        nome = ""
        email = ""

    contexto = {
        "erros": erros,
        "valores": {"nome": nome, "email": email},
        "sucesso": sucesso,
    }
    return render(request, "usuarios/cadastro.html", contexto)

def estatisticas_view(request: HttpRequest) -> HttpResponse:
    """Renderiza a tela de estatísticas com filtros de período e região."""
    data_inicio = request.GET.get("data_inicio", "")
    data_fim = request.GET.get("data_fim", "")
    erro = ""
    # Datas no formato AAAA-MM-DD (input type="date") comparam certo como texto.
    if data_inicio and data_fim and data_inicio > data_fim:
        erro = "A data inicial deve ser anterior à final."
    # shortcut: dados vazios até ligar ao app ocorrencias; trocar pela consulta.
    dados = {"total": 0, "por_tipo": [], "por_data": []}
    return render(
        request,
        "usuarios/estatisticas.html",
        {"erro": erro, "filtros": request.GET, "dados": dados},
    )
