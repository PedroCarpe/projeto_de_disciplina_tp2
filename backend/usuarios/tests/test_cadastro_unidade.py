from django.contrib.auth.models import User
from django.test import TestCase

from frontend.views import criar_usuario, validar_cadastro


class ValidarCadastroTests(TestCase):
    def test_dados_validos_nao_retornam_erros(self) -> None:
        erros = validar_cadastro(
            nome="Maria Silva",
            email="maria@exemplo.com",
            senha="senhaSegura123",
            confirmacao="senhaSegura123",
        )

        self.assertEqual(erros, {})

    def test_campos_vazios_retornam_erro_para_cada_campo(self) -> None:
        erros = validar_cadastro(nome="", email="", senha="", confirmacao="")

        self.assertEqual(
            erros,
            {
                "nome": "Informe seu nome completo.",
                "email": "Informe seu e-mail.",
                "senha": "Crie uma senha.",
                "confirmacao_senha": "Confirme sua senha.",
            },
        )

    def test_email_com_formato_invalido_retorna_erro(self) -> None:
        erros = validar_cadastro(
            nome="Maria Silva",
            email="email-invalido",
            senha="senhaSegura123",
            confirmacao="senhaSegura123",
        )

        self.assertEqual(erros, {"email": "Informe um e-mail válido."})

    def test_email_ja_cadastrado_nao_pode_ser_usado_novamente(self) -> None:
        User.objects.create_user(
            username="maria@exemplo.com",
            email="maria@exemplo.com",
            password="senhaSegura123",
        )

        erros = validar_cadastro(
            nome="Outra Maria",
            email="MARIA@exemplo.com",
            senha="outraSenha123",
            confirmacao="outraSenha123",
        )

        self.assertEqual(
            erros, {"email": "Este e-mail já está cadastrado."}
        )

    def test_senha_com_menos_de_oito_caracteres_retorna_erro(self) -> None:
        erros = validar_cadastro(
            nome="Maria Silva",
            email="maria@exemplo.com",
            senha="curta",
            confirmacao="curta",
        )

        self.assertEqual(
            erros, {"senha": "A senha deve ter pelo menos 8 caracteres."}
        )

    def test_confirmacao_diferente_da_senha_retorna_erro(self) -> None:
        erros = validar_cadastro(
            nome="Maria Silva",
            email="maria@exemplo.com",
            senha="senhaSegura123",
            confirmacao="senhaDiferente123",
        )

        self.assertEqual(erros, {"confirmacao_senha": "As senhas não coincidem."})


class CriarUsuarioTests(TestCase):
    def test_cria_usuario_com_nome_composto_e_senha_com_hash(self) -> None:
        resultado = criar_usuario(
            nome="Maria Silva Santos",
            email="maria@exemplo.com",
            senha="senhaSegura123",
        )

        usuario = User.objects.get(username="maria@exemplo.com")
        self.assertIsNone(resultado)
        self.assertEqual(usuario.email, "maria@exemplo.com")
        self.assertEqual(usuario.first_name, "Maria")
        self.assertEqual(usuario.last_name, "Silva Santos")
        self.assertTrue(usuario.check_password("senhaSegura123"))
        self.assertNotEqual(usuario.password, "senhaSegura123")

    def test_cria_usuario_com_sobrenome_vazio_quando_nome_tem_uma_palavra(
        self,
    ) -> None:
        criar_usuario(
            nome="Maria",
            email="maria@exemplo.com",
            senha="senhaSegura123",
        )

        usuario = User.objects.get(username="maria@exemplo.com")
        self.assertEqual(usuario.first_name, "Maria")
        self.assertEqual(usuario.last_name, "")
