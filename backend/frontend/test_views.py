from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class HomeViewTests(TestCase):
    def test_root_renderiza_mapa_de_ocorrencias(self) -> None:
        resposta = self.client.get("/")

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "base.html")
        self.assertTemplateUsed(resposta, "usuarios/inicio.html")
        self.assertContains(resposta, "Mapa de ocorrências")
        self.assertContains(resposta, "Buscar rua ou bairro")

    def test_mapa_tem_filtros_e_ocorrencia_destaque(self) -> None:
        resposta = self.client.get("/")

        self.assertContains(resposta, "Vias")
        self.assertContains(resposta, "Luz")
        self.assertContains(resposta, "Drenagem")
        self.assertContains(resposta, "Limpeza")
        self.assertContains(resposta, "Iluminação apagada")
        self.assertContains(resposta, "Em análise")
        self.assertContains(resposta, "Rua do Largo, 45")
        self.assertContains(resposta, "Ver detalhes")
        self.assertContains(resposta, "Acompanhar")
        self.assertContains(resposta, "Dados")
        self.assertContains(resposta, "Avisos")
        self.assertContains(resposta, "Perfil")


class LoginViewTests(TestCase):
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
        self.assertContains(response, "Ver mapa de ocorrências")
        self.assertContains(response, f'href="{reverse("inicio")}"')
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

    def test_login_marca_opcao_ativa_do_alternador(self) -> None:
        resposta = self.client.get(reverse("login"))
        conteudo = resposta.content.decode()

        self.assertContains(resposta, 'aria-selected="true" aria-current="page"')
        self.assertEqual(conteudo.count('aria-current="page"'), 1)
        self.assertContains(resposta, 'aria-selected="false">Criar conta')

    def test_login_toggle_de_senha_e_acessivel(self) -> None:
        resposta = self.client.get(reverse("login"))

        self.assertContains(resposta, 'type="button"')
        self.assertContains(resposta, 'aria-controls="id_senha"')
        self.assertContains(resposta, 'aria-label="Mostrar senha"')
        self.assertContains(resposta, 'aria-pressed="false"')
        self.assertContains(resposta, 'data-icon="eye"')
        self.assertContains(resposta, 'data-icon="eye-off"')

    def test_login_campos_usam_autocomplete_correto(self) -> None:
        resposta = self.client.get(reverse("login"))

        self.assertContains(resposta, 'type="email"')
        self.assertContains(resposta, 'autocomplete="email"')
        self.assertContains(resposta, 'type="password"')
        self.assertContains(resposta, 'autocomplete="current-password"')

    def test_login_nao_autentica_apenas_renderiza(self) -> None:
        resposta = self.client.post(
            reverse("login"),
            {"email": "maria@exemplo.com", "senha": "senhaSegura123"},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "usuarios/login.html")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_alternador_aponta_para_cadastro(self) -> None:
        resposta = self.client.get(reverse("login"))

        self.assertContains(resposta, f'href="{reverse("cadastro")}"')


class CadastroViewTests(TestCase):
    def test_cadastro_route_and_templates(self) -> None:
        self.assertEqual(reverse("cadastro"), "/cadastro/")

        response = self.client.get(reverse("cadastro"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base.html")
        self.assertTemplateUsed(response, "includes/logo.html")
        self.assertTemplateUsed(response, "usuarios/cadastro.html")

    def test_cadastro_has_essential_content(self) -> None:
        response = self.client.get(reverse("cadastro"))

        self.assertContains(response, "Nossa Rua")
        self.assertContains(response, "Nossa rua, cuidada por todos.")
        self.assertContains(response, "Registre, acompanhe e faça parte.")
        self.assertContains(response, f'href="{reverse("login")}"')
        self.assertContains(response, "Novo por aqui")
        self.assertContains(response, "Crie sua conta.")
        self.assertContains(response, "Nome completo")
        self.assertContains(response, "Confirmação de senha")
        self.assertNotContains(response, "Já tem uma conta?")

    def test_cadastro_keeps_form_integrity(self) -> None:
        response = self.client.get(reverse("cadastro"))
        conteudo = response.content.decode()

        self.assertContains(response, 'method="post"')
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertContains(response, 'name="nome"')
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="senha"')
        self.assertContains(response, 'name="confirmacao_senha"')
        self.assertContains(response, "data-senha-toggle")
        self.assertEqual(conteudo.count('aria-controls="id_'), 2)
        self.assertContains(response, 'aria-describedby="erro-nome"')
        self.assertContains(response, 'aria-describedby="erro-confirmacao-senha"')
        self.assertContains(response, "botao--primario")

    def test_cadastro_shows_validation_errors(self) -> None:
        response = self.client.post(
            reverse("cadastro"),
            {
                "nome": "",
                "email": "invalido",
                "senha": "123",
                "confirmacao_senha": "456",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Revise os campos destacados abaixo.")
        self.assertContains(response, "Informe seu nome completo.")
        self.assertContains(response, "Informe um e-mail válido.")
        self.assertContains(response, "A senha deve ter pelo menos 8 caracteres.")
        self.assertContains(response, "As senhas não coincidem.")
        self.assertContains(response, 'aria-invalid="true"')
        self.assertContains(response, "campo__grupo--invalido")
        self.assertNotContains(response, "data-aviso-erro hidden")

    def test_cadastro_reports_empty_required_fields(self) -> None:
        response = self.client.post(reverse("cadastro"), {})

        self.assertContains(response, "Informe seu e-mail.")
        self.assertContains(response, "Crie uma senha.")
        self.assertContains(response, "Confirme sua senha.")

    def test_cadastro_limpa_formulario_apos_sucesso(self) -> None:
        response = self.client.post(
            reverse("cadastro"),
            {
                "nome": "Maria Silva",
                "email": "maria@exemplo.com",
                "senha": "senhaSegura123",
                "confirmacao_senha": "senhaSegura123",
            },
        )

        conteudo = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "data-aviso-erro hidden")
        self.assertNotContains(response, 'class="campo__grupo campo__grupo--invalido"')
        self.assertEqual(conteudo.count('aria-invalid="true"'), 0)
        self.assertContains(response, "Conta criada com sucesso.")
        self.assertContains(response, 'value=""')

    def test_cadastro_cria_usuario_com_dados_validos(self) -> None:
        resposta = self.client.post(
            reverse("cadastro"),
            {
                "nome": "Maria Silva",
                "email": "maria@exemplo.com",
                "senha": "senhaSegura123",
                "confirmacao_senha": "senhaSegura123",
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Conta criada com sucesso.")

        usuario = User.objects.get(email="maria@exemplo.com")
        self.assertEqual(usuario.username, "maria@exemplo.com")
        self.assertEqual(usuario.get_full_name(), "Maria Silva")
        self.assertTrue(usuario.check_password("senhaSegura123"))
        self.assertNotEqual(usuario.password, "senhaSegura123")

    def test_cadastro_rejeita_email_duplicado(self) -> None:
        User.objects.create_user(
            username="joao@exemplo.com",
            email="joao@exemplo.com",
            password="senhaAntiga123",
            first_name="Joao",
            last_name="Silva",
        )

        resposta = self.client.post(
            reverse("cadastro"),
            {
                "nome": "Outro Joao",
                "email": "JOAO@exemplo.com",
                "senha": "senhaNova123",
                "confirmacao_senha": "senhaNova123",
            },
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, "Este e-mail já está cadastrado.")
        self.assertEqual(User.objects.count(), 1)
