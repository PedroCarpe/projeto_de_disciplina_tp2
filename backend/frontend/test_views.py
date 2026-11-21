from django.test import TestCase
from django.urls import reverse


class LoginViewTests(TestCase):
    def test_root_redirects_to_login(self) -> None:
        response = self.client.get("/")

        self.assertRedirects(response, reverse("login"))

    def test_login_page_uses_expected_templates(self) -> None:
        response = self.client.get(reverse("login"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "includes/logo.html")
        self.assertTemplateUsed(response, "usuarios/login.html")

    def test_login_page_has_essential_content(self) -> None:
        response = self.client.get(reverse("login"))

        self.assertContains(response, "Nossa Rua")
        self.assertContains(response, "Nossa rua, cuidada por todos.")
        self.assertContains(response, "Registre, acompanhe e faça parte.")
        self.assertContains(response, "Explorar como visitante")
        self.assertContains(response, "Acesso ao sistema")
        self.assertContains(response, "Bom ter você de volta.")
        self.assertContains(response, "Entre para acompanhar o que importa para você.")
        self.assertContains(response, "Entrar")
        self.assertContains(response, "Criar conta")

    def test_login_page_keeps_form_integrity(self) -> None:
        response = self.client.get(reverse("login"))

        self.assertContains(response, 'method="post"')
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="senha"')
        self.assertContains(response, "data-senha-toggle")

    def test_login_page_has_no_extra_options_or_footer(self) -> None:
        response = self.client.get(reverse("login"))

        for texto in (
            "Lembrar meu acesso",
            "Esqueceu a senha?",
            "Cadastre-se",
            "Seus dados ficam protegidos",
        ):
            self.assertNotContains(response, texto)

    def test_login_page_uses_shared_components(self) -> None:
        response = self.client.get(reverse("login"))

        self.assertContains(response, 'class="autenticacao"')
        self.assertContains(response, "marca__icone")
        self.assertContains(response, "marca__pin")
        self.assertContains(response, "marca__brilho")
        self.assertContains(response, 'class="marca__ponto"')
        self.assertContains(response, "linha-mapa")
        self.assertContains(response, "etiqueta__icone")
        self.assertContains(response, "apresentacao__conteudo")
        self.assertContains(response, "alternador__opcao--ativa")
        self.assertContains(response, "acesso__titulo")
        self.assertContains(response, "botao--primario")
