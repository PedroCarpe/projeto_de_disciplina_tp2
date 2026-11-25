from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.test import TestCase


class AutenticacaoUsuarioTests(TestCase):
    def setUp(self) -> None:
        self.email = "maria@exemplo.com"
        self.senha = "senhaSegura123"
        User.objects.create_user(
            username=self.email,
            email=self.email,
            password=self.senha,
        )

    def test_autentica_usuario_com_email_e_senha_validos(self) -> None:
        usuario = authenticate(username=self.email, password=self.senha)

        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.username, self.email)

    def test_rejeita_senha_incorreta(self) -> None:
        usuario = authenticate(username=self.email, password="senhaErrada123")

        self.assertIsNone(usuario)

    def test_rejeita_email_inexistente(self) -> None:
        usuario = authenticate(
            username="inexistente@exemplo.com", password=self.senha
        )

        self.assertIsNone(usuario)

    def test_rejeita_campos_vazios(self) -> None:
        usuario = authenticate(username="", password="")

        self.assertIsNone(usuario)
