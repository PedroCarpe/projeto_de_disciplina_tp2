import re
from pathlib import Path

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase, override_settings
from django.urls import reverse


class HomeVisitanteTests(TestCase):
    def test_home_publica_renderiza_template_e_mensagem(self) -> None:
        resposta = self.client.get(reverse("inicio"))

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "base.html")
        self.assertTemplateUsed(resposta, "usuarios/inicio.html")
        self.assertContains(resposta, "Nossa Rua.")
        self.assertContains(resposta, "Uma cidade melhor")
        self.assertContains(resposta, "por aqui.")

    def test_visitante_tem_acoes_de_entrar_e_cadastrar(self) -> None:
        resposta = self.client.get(reverse("inicio"))

        self.assertContains(resposta, f'href="{reverse("login")}"')
        self.assertContains(resposta, f'href="{reverse("cadastro")}"')
        self.assertContains(resposta, "Entrar")
        self.assertContains(resposta, "Cadastrar")
        self.assertContains(resposta, "Criar conta para participar")

    def test_visitante_registrar_encaminha_para_login(self) -> None:
        conteudo = self.client.get(reverse("inicio")).content.decode()

        self.assertIn(f'href="{reverse("login")}"', conteudo)
        self.assertNotIn("Registrar ocorrência", conteudo)

    def test_home_nao_carrega_leaflet_nem_componente_do_mapa(self) -> None:
        conteudo = self.client.get(reverse("inicio")).content.decode()

        self.assertNotIn("leaflet", conteudo)
        self.assertNotIn("home_mapa.js", conteudo)
        self.assertNotIn("home-mapa-canvas", conteudo)

    def test_visitante_nao_ve_acoes_restritas(self) -> None:
        resposta = self.client.get(reverse("inicio"))

        restritas = (
            "Sair",
            "Minhas ocorrências",
            "Acompanhando",
            "Notificações",
            "Sua cidade, mais bem cuidada.",
        )
        for texto in restritas:
            self.assertNotContains(resposta, texto)
        self.assertNotContains(resposta, 'href="#"')

    def test_home_visitante_usa_estrutura_compacta(self) -> None:
        resposta = self.client.get(reverse("inicio"))

        self.assertContains(resposta, 'class="home home--visitante ')
        self.assertNotContains(resposta, "Explore sem precisar entrar")
        self.assertNotContains(resposta, "home__nota")

    def test_visitante_ve_tres_cartoes_de_navegacao(self) -> None:
        resposta = self.client.get(reverse("inicio"))

        self.assertContains(resposta, "Explore a plataforma")
        conteudo = resposta.content.decode()
        self.assertIn(
            'class="home-cartoes grid grid-cols-1 gap-3 md:grid-cols-3"', conteudo
        )
        self.assertEqual(
            len(re.findall(r'class="[^"]*\bhome-cartao\b[^"]*"', conteudo)), 3
        )
        self.assertContains(resposta, "Mapa")
        self.assertContains(resposta, "Estatísticas")
        self.assertContains(resposta, "Alertas")

    def test_cartao_mapa_aponta_para_rota_real(self) -> None:
        resposta = self.client.get(reverse("inicio"))

        self.assertContains(resposta, f'href="{reverse("mapa")}" class="home-cartao ')
        self.assertContains(resposta, "Explorar mapa")

    def test_cartao_estatisticas_aponta_para_rota_real(self) -> None:
        resposta = self.client.get(reverse("inicio"))

        self.assertContains(
            resposta, f'href="{reverse("estatisticas")}" class="home-cartao '
        )

    def test_visitante_ve_dois_ctas_reais(self) -> None:
        conteudo = self.client.get(reverse("inicio")).content.decode()

        self.assertIn(f'href="{reverse("cadastro")}"', conteudo)
        self.assertIn(f'href="{reverse("mapa")}"', conteudo)
        self.assertIn("Criar conta para participar", conteudo)
        self.assertIn("Explorar mapa", conteudo)

    def test_botoes_indisponiveis_do_visitante_sao_explicitos(self) -> None:
        conteudo = self.client.get(reverse("inicio")).content.decode()

        self.assertEqual(conteudo.count('disabled aria-disabled="true"'), 0)
        self.assertNotIn('class="home-nav"', conteudo)
        self.assertNotIn('class="home-nav__item"', conteudo)


class HomeAutenticadoTests(TestCase):
    def setUp(self) -> None:
        self.usuario = User.objects.create_user(
            username="maria@exemplo.com",
            email="maria@exemplo.com",
            password="senhaSegura123",
            first_name="Maria",
        )
        self.client.force_login(self.usuario)

    def test_home_autenticada_traz_saudacao_e_mensagem(self) -> None:
        resposta = self.client.get(reverse("inicio"))

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "base.html")
        self.assertTemplateUsed(resposta, "usuarios/inicio.html")
        self.assertContains(resposta, "Olá, Maria")
        self.assertContains(resposta, "Sua cidade,")
        self.assertContains(resposta, "mais bem cuidada.")
        self.assertContains(resposta, "Nossa Rua.")
        self.assertContains(resposta, 'class="home home--autenticado ')

    def test_autenticado_ve_acoes_e_cartoes(self) -> None:
        resposta = self.client.get(reverse("inicio"))

        permitidos = (
            "Registrar ocorrência",
            "Mapa",
            "Estatísticas",
            "Alertas",
            "Sair",
        )
        for texto in permitidos:
            self.assertContains(resposta, texto)
        self.assertNotContains(resposta, "Notificações")
        self.assertNotContains(resposta, 'href="#"')

    def test_home_autenticada_nao_carrega_leaflet(self) -> None:
        conteudo = self.client.get(reverse("inicio")).content.decode()

        self.assertNotIn("leaflet", conteudo)
        self.assertNotIn("home_mapa.js", conteudo)
        self.assertNotIn("home-mapa-canvas", conteudo)

    def test_cta_registrar_leva_para_tela_de_registro(self) -> None:
        conteudo = self.client.get(reverse("inicio")).content.decode()

        self.assertIn(f'href="{reverse("registrar_ocorrencia")}"', conteudo)
        self.assertNotIn('disabled aria-disabled="true"', conteudo)

    def test_cta_indisponivel_nao_cita_integracao(self) -> None:
        conteudo = self.client.get(reverse("inicio")).content.decode()

        self.assertIn("Registrar ocorrência", conteudo)
        self.assertNotIn("O registro de ocorrências ainda será integrado.", conteudo)

    def test_autenticado_nao_ve_links_de_login_e_cadastro(self) -> None:
        resposta = self.client.get(reverse("inicio"))

        self.assertNotContains(resposta, f'href="{reverse("login")}"')
        self.assertNotContains(resposta, f'href="{reverse("cadastro")}"')
        self.assertNotContains(resposta, "Criar conta para participar")
        self.assertNotContains(resposta, "Uma cidade melhor começa por aqui.")

    def test_saida_usa_post_e_encaminha_para_home(self) -> None:
        self.assertEqual(reverse("logout"), "/sair/")
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)

        resposta = self.client.post(reverse("logout"))

        self.assertRedirects(resposta, reverse("inicio"))
        self.assertNotIn("_auth_user_id", self.client.session)
        self.assertContains(self.client.get(reverse("inicio")), "Entrar")


class HomeVinculoAdministracaoTests(TestCase):
    def test_administrador_ve_botao_para_o_painel(self) -> None:
        usuario = User.objects.create_user(
            username="admin@exemplo.com",
            email="admin@exemplo.com",
            password="senhaSegura123",
            is_staff=True,
        )
        self.client.force_login(usuario)

        resposta = self.client.get(reverse("inicio"))

        self.assertContains(resposta, f'href="{reverse("administracao:painel")}"')
        self.assertContains(resposta, "Administração")

    def test_usuario_comum_nao_ve_botao_para_o_painel(self) -> None:
        usuario = User.objects.create_user(
            username="comum@exemplo.com",
            email="comum@exemplo.com",
            password="senhaSegura123",
        )
        self.client.force_login(usuario)

        resposta = self.client.get(reverse("inicio"))

        self.assertNotContains(resposta, reverse("administracao:painel"))
        self.assertNotContains(resposta, "Administração")

    def test_visitante_nao_ve_botao_para_o_painel(self) -> None:
        resposta = self.client.get(reverse("inicio"))

        self.assertNotContains(resposta, reverse("administracao:painel"))
        self.assertNotContains(resposta, "Administração")


class HomeAlertasTests(TestCase):
    def test_cartao_alertas_aponta_para_notificacoes(self) -> None:
        conteudo = self.client.get(reverse("inicio")).content.decode()

        cartao = re.search(
            rf'<a[^>]*href="{reverse("notificacoes")}"[^>]*home-cartao[^>]*>',
            conteudo,
        )
        self.assertIsNotNone(cartao)
        self.assertNotIn("disabled", cartao.group(0))

    def test_cartao_alertas_continua_disponivel_para_autenticado(self) -> None:
        usuario = User.objects.create_user(
            username="comum@exemplo.com",
            email="comum@exemplo.com",
            password="senha123",
        )
        self.client.force_login(usuario)

        resposta = self.client.get(reverse("inicio"))

        self.assertContains(resposta, f'href="{reverse("notificacoes")}"')
        self.assertContains(resposta, "Alertas")


class MapaViewTests(TestCase):
    def test_mapa_e_publico_e_renderiza_componente(self) -> None:
        resposta = self.client.get(reverse("mapa"))

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "base.html")
        self.assertTemplateUsed(resposta, "usuarios/mapa.html")
        self.assertTemplateUsed(resposta, "includes/home_mapa.html")
        self.assertContains(resposta, "Mapa de ocorrências")
        self.assertContains(resposta, 'id="home-mapa-canvas"')

    def test_mapa_tem_busca_filtros_e_cartao_de_detalhes(self) -> None:
        conteudo = self.client.get(reverse("mapa")).content.decode()

        self.assertIn("Buscar região, bairro ou endereço...", conteudo)
        for filtro in ("categoria", "status", "periodo"):
            self.assertIn(f'data-filtro="{filtro}"', conteudo)
        for texto in (
            "Tipo de ocorrência",
            "Aplicar filtros",
            "Minha localização",
            "Acompanhar",
            "data-mapa-detalhe",
            "Ver detalhes",
        ):
            self.assertIn(texto, conteudo)

    def test_acoes_indisponiveis_do_mapa_nao_citam_integracao(self) -> None:
        conteudo = self.client.get(reverse("mapa")).content.decode()

        self.assertIn("Ver detalhes", conteudo)
        self.assertIn("Acompanhar", conteudo)
        self.assertNotIn("Página de detalhes ainda será integrada.", conteudo)
        self.assertNotIn("Recurso de acompanhamento ainda será integrado.", conteudo)

    def test_mapa_carrega_leaflet_uma_unica_vez(self) -> None:
        conteudo = self.client.get(reverse("mapa")).content.decode()

        self.assertEqual(conteudo.count("leaflet@1.9.4/dist/leaflet.css"), 1)
        self.assertEqual(conteudo.count("leaflet@1.9.4/dist/leaflet.js"), 1)
        self.assertEqual(conteudo.count("js/home_mapa.js"), 1)

    def test_mapa_recebe_configuracao_padrao(self) -> None:
        resposta = self.client.get(reverse("mapa"))

        self.assertIn("mapa_config", resposta.context)
        self.assertEqual(
            resposta.context["mapa_config"]["centro"],
            {"lat": -23.5505, "lng": -46.6333},
        )
        self.assertEqual(resposta.context["mapa_config"]["zoom"], 13)
        self.assertEqual(resposta.context["mapa_config"]["ocorrencias"], [])

    @override_settings(
        MAPA_PADRAO={"lat": -15.7939, "lng": -47.8828, "zoom": 12}
    )
    def test_regiao_padrao_e_configuravel_na_pagina_do_mapa(self) -> None:
        resposta = self.client.get(reverse("mapa"))

        self.assertContains(resposta, "-15.7939")
        self.assertContains(resposta, "-47.8828")
        self.assertContains(resposta, '"zoom": 12')

    def test_mapa_disponivel_para_autenticado(self) -> None:
        usuario = User.objects.create_user(
            username="joao@exemplo.com",
            email="joao@exemplo.com",
            password="senhaSegura123",
        )
        self.client.force_login(usuario)

        resposta = self.client.get(reverse("mapa"))

        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'id="home-mapa-canvas"')

    def test_mapa_tem_link_de_volta_para_home(self) -> None:
        resposta = self.client.get(reverse("mapa"))

        self.assertContains(resposta, f'href="{reverse("inicio")}"')


class HomeCssTests(SimpleTestCase):
    caminho_css = Path(__file__).resolve().parents[1] / "static" / "css" / "app.css"

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.css = cls.caminho_css.read_text(encoding="utf-8")

    def test_identidade_e_foco_visivel_sao_preservados(self) -> None:
        self.assertIn('--fonte-base: "Nunito"', self.css)
        self.assertIn(":focus-visible", self.css)

    def test_mapa_e_alto_no_desktop_e_compacto_no_celular(self) -> None:
        conteudo = self.client.get(reverse("mapa")).content.decode()

        self.assertIn('class="home-mapa__area relative h-[26rem]', conteudo)
        self.assertIn("lg:h-[520px]", conteudo)
        self.assertIn("xl:h-[550px]", conteudo)

    def test_mapa_leaflet_usa_tokens_e_nao_bloqueia_interacao(self) -> None:
        self.assertIn(".leaflet-container", self.css)
        self.assertIn(".home-mapa__vazio", self.css)
        self.assertIn("pointer-events: none", self.css)
        self.assertIn("var(--fonte-base)", self.css)
        self.assertIn(".home-mapa__area.leaflet-container .leaflet-bar a", self.css)

    def test_cartoes_sao_compactos_e_acessiveis(self) -> None:
        self.assertIn(".home-cartoes", self.css)
        self.assertIn(".home-cartao", self.css)
        self.assertIn("min-height: 2.75rem", self.css)

    def test_navegacao_inferior_foi_removida(self) -> None:
        self.assertNotIn(".home-nav", self.css)

    def test_marca_tem_alvo_de_toque_confortavel(self) -> None:
        padrao = r"\.marca \{[^}]*min-height: 2\.75rem"

        self.assertIsNotNone(re.search(padrao, self.css, re.DOTALL))


class HomeMapaJsTests(SimpleTestCase):
    caminho_js = Path(__file__).resolve().parents[1] / "static" / "js" / "home_mapa.js"

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.js = cls.caminho_js.read_text(encoding="utf-8")

    def test_localizacao_solicitada_apenas_no_clique(self) -> None:
        self.assertIn('data-mapa-localizacao', self.js)
        self.assertIn('addEventListener("click"', self.js)
        self.assertIn("getCurrentPosition", self.js)
        self.assertNotIn("getCurrentPosition()", self.js)

    def test_falha_de_localizacao_mantem_mapa_utilizavel(self) -> None:
        self.assertIn("setView", self.js)
        self.assertIn("function onErro", self.js)
        self.assertIn("erro", self.js)

    def test_interface_prepara_ocorrencias_reais(self) -> None:
        for campo in ("latitude", "longitude", "tipo", "data", "status"):
            self.assertIn(campo, self.js)
        self.assertIn("L.layerGroup", self.js)
        self.assertIn("L.divIcon", self.js)
        self.assertIn("data-mapa-detalhe", self.js)
        self.assertIn("data-detalhe-descricao", self.js)
        self.assertIn("data-mapa-aplicar", self.js)
        self.assertIn("data-filtro", self.js)
        self.assertIn("calcada", self.js)
        self.assertIn("lixo", self.js)

    def test_script_tem_guarda_contra_inicializacao_dupla(self) -> None:
        self.assertIn("NossaRua", self.js)
        self.assertIn("mapaHome", self.js)

    def test_tiles_respeitam_politica_do_osm_e_tem_fallback_tecnico(self) -> None:
        self.assertIn('"https://tile.openstreetmap.org/{z}/{x}/{y}.png"', self.js)
        self.assertLess(
            self.js.index("tile.openstreetmap.org"),
            self.js.index("basemaps.cartocdn.com"),
        )
        self.assertNotIn("referrerPolicy:", self.js)
        self.assertNotIn("no-referrer", self.js)
        self.assertIn("tileerror", self.js)
        self.assertIn("tileload", self.js)
        self.assertIn("falha técnica", self.js)
        self.assertIn("basemaps.cartocdn.com", self.js)

    def test_fallback_de_tiles_preserva_mapa_e_ocorrencias(self) -> None:
        self.assertIn("function trocarProvedor", self.js)
        self.assertIn("removeLayer", self.js)
        self.assertIn("falhasDeTile", self.js)
        self.assertIn("O mapa foi ajustado para continuar funcionando.", self.js)
        self.assertNotIn("provedor alternativo", self.js)


class TailwindFrontendTests(TestCase):
    caminho_base = Path(__file__).resolve().parents[1] / "templates" / "base.html"

    def test_base_carrega_tailwind_e_politica_de_referrer(self) -> None:
        base = self.caminho_base.read_text(encoding="utf-8")

        self.assertEqual(base.count("https://cdn.tailwindcss.com"), 1)
        self.assertIn("tailwind.config =", base)
        self.assertIn(
            '<meta name="referrer" content="strict-origin-when-cross-origin" />', base
        )
        self.assertNotIn('content="no-referrer"', base)
        for trecho in (
            'creme: "#fbf8f3"',
            'verde: "#2f6b55"',
            '"verde-escuro": "#1f5240"',
            'salvia: "#d5ebdf"',
            '"Nunito"',
            "preflight: false",
        ):
            self.assertIn(trecho, base)
        self.assertNotIn("blue", base.lower())

    def test_home_tem_estrutura_de_apresentacao_e_navegacao(self) -> None:
        conteudo = self.client.get(reverse("inicio")).content.decode()

        for trecho in (
            "PARTICIPE DA SUA CIDADE",
            "por aqui.",
            "Pequenas atitudes. Grandes mudanças.",
            "Sua rua. Sua voz.",
            "CONEXÕES QUE TRANSFORMAM",
            "CONECTE-SE COM A SUA REGIÃO",
            "O primeiro passo para transformar está aqui.",
            "Uma cidade melhor é uma construção de todos.",
            'class="home-cartoes',
        ):
            self.assertIn(trecho, conteudo)
        self.assertEqual(
            len(re.findall(r'class="[^"]*\bhome-cartao\b[^"]*"', conteudo)), 3
        )


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
        self.assertNotContains(response, "Ver mapa de ocorrências")
        self.assertNotContains(response, f'href="{reverse("mapa")}"')
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

    def test_login_com_credenciais_validas_autentica_e_redireciona(self) -> None:
        email = "maria@exemplo.com"
        senha = "senhaSegura123"
        User.objects.create_user(
            username=email,
            email=email,
            password=senha,
        )

        resposta = self.client.post(
            reverse("login"),
            {"email": email, "senha": senha},
        )

        self.assertRedirects(resposta, reverse("inicio"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_login_com_senha_incorreta_nao_autentica(self) -> None:
        email = "maria@exemplo.com"
        User.objects.create_user(
            username=email,
            email=email,
            password="senhaSegura123",
        )

        resposta = self.client.post(
            reverse("login"),
            {"email": email, "senha": "senhaErrada123"},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "usuarios/login.html")
        self.assertContains(resposta, "E-mail ou senha inválidos.")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_login_com_email_inexistente_nao_autentica(self) -> None:
        resposta = self.client.post(
            reverse("login"),
            {"email": "inexistente@exemplo.com", "senha": "senhaSegura123"},
        )

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "usuarios/login.html")
        self.assertContains(resposta, "E-mail ou senha inválidos.")
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

class EstatisticasViewTests(TestCase):
    def test_estatisticas_e_publica_e_usa_template(self) -> None:
        resposta = self.client.get(reverse("estatisticas"))

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "usuarios/estatisticas.html")

    def test_estatisticas_tem_filtros_de_periodo_e_regiao(self) -> None:
        resposta = self.client.get(reverse("estatisticas"))

        self.assertContains(resposta, 'name="data_inicio"')
        self.assertContains(resposta, 'name="data_fim"')
        self.assertContains(resposta, 'name="regiao"')

    def test_sem_ocorrencias_mostra_aviso(self) -> None:
        resposta = self.client.get(reverse("estatisticas"))

        self.assertContains(resposta, "Nenhuma ocorrência registrada no período.")

    def test_periodo_invertido_mostra_erro(self) -> None:
        resposta = self.client.get(
            reverse("estatisticas"),
            {"data_inicio": "2026-11-30", "data_fim": "2026-11-01"},
        )

        self.assertContains(resposta, "A data inicial deve ser anterior à final.")

    def test_estatisticas_entrega_dados_vazios_para_graficos(self) -> None:
        resposta = self.client.get(reverse("estatisticas"))

        self.assertContains(resposta, 'id="estatisticas-dados"')
        self.assertEqual(
            resposta.context["dados"],
            {"total": 0, "por_tipo": [], "por_data": []},
        )

    def test_estatisticas_tem_total_e_dois_graficos(self) -> None:
        resposta = self.client.get(reverse("estatisticas"))

        self.assertContains(resposta, "data-total")
        self.assertContains(resposta, 'data-grafico="tipo"')
        self.assertContains(resposta, 'data-grafico="tempo"')

    def test_estatisticas_carrega_chartjs_e_script(self) -> None:
        resposta = self.client.get(reverse("estatisticas"))

        self.assertContains(resposta, "chart.umd.min.js")
        self.assertContains(resposta, "js/estatisticas.js")

class EstatisticasJsTests(SimpleTestCase):
    caminho_js = (
        Path(__file__).resolve().parents[1] / "static" / "js" / "estatisticas.js"
    )

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.js = cls.caminho_js.read_text(encoding="utf-8")

    def test_le_dados_do_json_script(self) -> None:
        self.assertIn('getElementById("estatisticas-dados")', self.js)
        self.assertIn("JSON.parse", self.js)

    def test_desenha_dois_graficos(self) -> None:
        self.assertEqual(self.js.count("new Chart("), 2)

    def test_pagina_funciona_sem_chartjs(self) -> None:
        self.assertIn('typeof Chart === "undefined"', self.js)
