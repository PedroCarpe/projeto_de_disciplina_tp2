from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CadastroUsuarioIntegracaoTests(TestCase):
    def test_exibe_formulario_de_cadastro(self):
        response = self.client.get(reverse("usuarios:cadastro"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="username"')
        self.assertContains(response, 'name="password1"')
        self.assertContains(response, 'name="password2"')

    def test_cadastra_usuario_pelo_formulario(self):
        response = self.client.post(
            reverse("usuarios:cadastro"),
            {
                "username": "ana",
                "password1": "Senha-forte-2026!",
                "password2": "Senha-forte-2026!",
            },
        )

        user = get_user_model().objects.get(username="ana")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Cadastro realizado com sucesso")
        self.assertTrue(user.check_password("Senha-forte-2026!"))
        self.assertNotEqual(user.password, "Senha-forte-2026!")

    def test_nao_cadastra_senhas_diferentes(self):
        response = self.client.post(
            reverse("usuarios:cadastro"),
            {
                "username": "ana",
                "password1": "Senha-forte-2026!",
                "password2": "Outra-senha-2026!",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(get_user_model().objects.filter(username="ana").exists())
