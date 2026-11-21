from django.shortcuts import render

from usuarios.forms import CadastroUsuarioForm


def cadastro(request):
    enviou_formulario = request.method == "POST"
    dados = request.POST if enviou_formulario else None
    form = CadastroUsuarioForm(dados)

    if enviou_formulario and form.is_valid():
        form.save()
        return render(
            request,
            "usuarios/cadastro.html",
            {"form": CadastroUsuarioForm(), "sucesso": True},
        )

    return render(
        request,
        "usuarios/cadastro.html",
        {"form": form, "sucesso": False},
    )
