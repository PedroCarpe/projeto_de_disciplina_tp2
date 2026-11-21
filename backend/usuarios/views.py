from django.shortcuts import render

from usuarios.forms import CadastroUsuarioForm


def cadastro(request):
    if request.method == "POST":
        form = CadastroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return render(
                request,
                "usuarios/cadastro.html",
                {"form": CadastroUsuarioForm(), "sucesso": True},
            )
    else:
        form = CadastroUsuarioForm()

    return render(request, "usuarios/cadastro.html", {"form": form})
