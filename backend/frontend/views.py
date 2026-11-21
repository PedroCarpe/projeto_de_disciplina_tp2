from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def login_view(request: HttpRequest) -> HttpResponse:
    """Renderiza a tela de login (apresentação, sem autenticação ainda)."""
    return render(request, "usuarios/login.html")


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
