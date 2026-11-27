import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse

URL_NOTIFICACOES = reverse("notificacoes")


class AcessoTests(TestCase):
    def test_visitante_e_encaminhado_para_login_com_next(self) -> None:
        resposta = self.client.get(URL_NOTIFICACOES)

        self.assertEqual(resposta.status_code, 302)
        destino = urlparse(resposta.url)
        self.assertEqual(destino.path, reverse("login"))
        self.assertEqual(parse_qs(destino.query).get("next"), [URL_NOTIFICACOES])

    def test_usuario_comum_pode_acessar_sem_is_staff(self) -> None:
        usuario = User.objects.create_user(
            username="comum@exemplo.com",
            email="comum@exemplo.com",
            password="senha123",
        )
        self.assertFalse(usuario.is_staff)
        self.client.force_login(usuario)

        resposta = self.client.get(URL_NOTIFICACOES)

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "base.html")
        self.assertTemplateUsed(resposta, "usuarios/notificacoes.html")


class EstruturaTests(TestCase):
    def setUp(self) -> None:
        usuario = User.objects.create_user(
            username="comum@exemplo.com",
            email="comum@exemplo.com",
            password="senha123",
        )
        self.client.force_login(usuario)
        self.resposta = self.client.get(URL_NOTIFICACOES)
        self.html = self.resposta.content.decode()

    def test_painel_tem_tres_abas_acessiveis(self) -> None:
        self.assertIn('role="tablist"', self.html)

        for aba in ("notificacoes", "favoritos", "preferencias"):
            with self.subTest(aba=aba):
                self.assertIn(f'data-notificacao-aba="{aba}"', self.html)
                self.assertIn(f'aria-controls="painel-{aba}"', self.html)
                self.assertIn(f'id="aba-{aba}"', self.html)

        self.assertRegex(
            self.html,
            r'data-notificacao-aba="notificacoes"[^>]*aria-selected="true"',
        )
        for aba in ("favoritos", "preferencias"):
            with self.subTest(aba=aba):
                self.assertRegex(
                    self.html,
                    rf'data-notificacao-aba="{aba}"[^>]*aria-selected="false"',
                )

    def test_painel_renderiza_includes_das_tres_abas(self) -> None:
        includes = {
            "notificacoes": "alertas",
            "favoritos": "favoritos",
            "preferencias": "preferencias",
        }
        for aba, include in includes.items():
            with self.subTest(aba=aba):
                self.assertTemplateUsed(
                    self.resposta, f"usuarios/includes/{include}.html"
                )
                self.assertIn(f'id="painel-{aba}"', self.html)
                self.assertIn(f'data-notificacao-painel="{aba}"', self.html)

    def test_apenas_aba_inicial_visivel(self) -> None:
        self.assertNotRegex(self.html, r'id="painel-notificacoes"[^>]*\bhidden\b')
        for aba in ("favoritos", "preferencias"):
            with self.subTest(aba=aba):
                self.assertRegex(self.html, rf'id="painel-{aba}"[^>]*\bhidden\b')

    def test_painel_reaproveita_identidade_e_carrega_script(self) -> None:
        self.assertTemplateUsed(self.resposta, "includes/logo.html")
        self.assertContains(self.resposta, "Nossa Rua.")
        self.assertContains(self.resposta, "static/js/notificacoes.js")
        self.assertContains(self.resposta, "defer")
        self.assertNotContains(self.resposta, "leaflet")
        self.assertNotContains(self.resposta, 'href="#"')

    def test_alertas_aparece_como_secao_ativa(self) -> None:
        self.assertContains(self.resposta, "Alertas")
        self.assertContains(self.resposta, 'aria-current="page"')

    def test_painel_nao_expõe_detalhes_de_desenvolvimento(self) -> None:
        for trecho in (
            "Integração pendente",
            "Integrações pendentes",
            "integração com o backend",
            "integração estiver disponível",
            "serão salvas pelo backend",
        ):
            with self.subTest(trecho=trecho):
                self.assertNotContains(self.resposta, trecho)


class ConteudoDasAbasTests(TestCase):
    def setUp(self) -> None:
        usuario = User.objects.create_user(
            username="comum@exemplo.com",
            email="comum@exemplo.com",
            password="senha123",
        )
        self.client.force_login(usuario)
        self.resposta = self.client.get(URL_NOTIFICACOES)
        self.html = self.resposta.content.decode()

    def painel(self, nome: str) -> str:
        trecho = re.search(
            rf'id="painel-{nome}".*?</section>', self.html, re.DOTALL
        )
        self.assertIsNotNone(trecho)
        return trecho.group(0)

    def test_notificacoes_tem_estado_vazio_e_explicacao(self) -> None:
        for texto in (
            "Você ainda não recebeu nenhuma notificação",
            "atualizações das ocorrências",
            "acompanha",
            "aparecerão aqui.",
        ):
            with self.subTest(texto=texto):
                self.assertContains(self.resposta, texto)
        self.assertNotContains(self.resposta, "integração com o backend")

    def test_favoritos_tem_estado_vazio_e_link_para_o_mapa(self) -> None:
        self.assertContains(self.resposta, "Nenhuma ocorrência favoritada")
        self.assertContains(
            self.resposta, "Explore o mapa para conhecer as ocorrências"
        )
        self.assertIn(f'href="{reverse("mapa")}"', self.painel("favoritos"))
        self.assertNotContains(self.resposta, "integração estiver disponível")

    def test_preferencias_nao_simula_salvamento(self) -> None:
        self.assertContains(self.resposta, "Salvar preferências")
        self.assertContains(self.resposta, "Suas preferências de acompanhamento")
        preferencias = self.painel("preferencias")
        self.assertIn("disabled", preferencias)
        self.assertNotIn("<form", preferencias)
        self.assertNotIn("action=", preferencias)
        self.assertNotIn("localStorage", preferencias)
        self.assertNotIn("serão salvas pelo backend", preferencias)


class NotificacoesJsTests(SimpleTestCase):
    caminho_js = (
        Path(__file__).resolve().parents[2] / "static" / "js" / "notificacoes.js"
    )

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.js = cls.caminho_js.read_text(encoding="utf-8")

    def test_alternancia_abas_com_aria_e_teclado(self) -> None:
        for trecho in (
            "data-notificacao-aba",
            'role="tab"',
            "aria-selected",
            "hidden",
            "tabIndex",
            'addEventListener("click"',
            'addEventListener("keydown"',
            "ArrowRight",
            "ArrowLeft",
            "Home",
            "End",
        ):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, self.js)

    def test_estado_visual_das_abas_e_alternado(self) -> None:
        for trecho in (
            'classList.toggle("bg-verde-escuro", ativa)',
            'classList.toggle("text-white", ativa)',
            'classList.toggle("bg-white", !ativa)',
            'classList.toggle("text-verde-escuro", !ativa)',
        ):
            with self.subTest(trecho=trecho):
                self.assertIn(trecho, self.js)

    def test_interacao_e_apenas_visual(self) -> None:
        for trecho in (
            "fetch(",
            "XMLHttpRequest",
            "localStorage",
            "sessionStorage",
            "form.submit(",
        ):
            with self.subTest(trecho=trecho):
                self.assertNotIn(trecho, self.js)
