from pathlib import Path

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse


class RegistrarOcorrenciaTests(TestCase):
    def setUp(self) -> None:
        self.usuario = User.objects.create_user(
            username="ana@exemplo.com",
            email="ana@exemplo.com",
            password="senhaSegura123",
        )

    def test_visitante_e_encaminhado_para_login(self) -> None:
        resposta = self.client.get(reverse("registrar_ocorrencia"))

        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("login"), resposta.url)

    def test_autenticado_ve_formulario_de_registro(self) -> None:
        self.client.force_login(self.usuario)

        resposta = self.client.get(reverse("registrar_ocorrencia"))

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "base.html")
        self.assertTemplateUsed(resposta, "ocorrencias/registrar_ocorrencia.html")
        self.assertContains(resposta, "Registrar ocorrência")
        for campo in ("tipo", "descricao", "latitude", "longitude"):
            self.assertContains(resposta, f'name="{campo}"')

    def test_formulario_usa_componentes_do_design_system(self) -> None:
        self.client.force_login(self.usuario)

        resposta = self.client.get(reverse("registrar_ocorrencia"))

        self.assertTemplateUsed(resposta, "includes/logo.html")
        for classe in ("formulario", "campo__controle", "botao botao--primario"):
            self.assertContains(resposta, f'class="{classe}')
        self.assertContains(resposta, f'href="{reverse("inicio")}"')
        for tipo in ("buraco", "iluminacao", "lixo", "calcada", "outros"):
            self.assertContains(resposta, f'value="{tipo}"')

    def test_formulario_oferece_tipos_ampliados(self) -> None:
        self.client.force_login(self.usuario)

        resposta = self.client.get(reverse("registrar_ocorrencia"))

        for tipo in ("sinalizacao", "arvore", "esgoto", "alagamento", "vandalismo"):
            self.assertContains(resposta, f'value="{tipo}"')
        self.assertContains(
            resposta,
            '<option value="outros">Outros</option>',
            html=True,
        )

    def test_formulario_carrega_script_de_localizacao(self) -> None:
        self.client.force_login(self.usuario)

        resposta = self.client.get(reverse("registrar_ocorrencia"))

        self.assertContains(resposta, "js/registrar_ocorrencia.js", count=1)


class RegistrarOcorrenciaJsTests(SimpleTestCase):
    caminho_js = (
        Path(__file__).resolve().parents[2]
        / "static"
        / "js"
        / "registrar_ocorrencia.js"
    )

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.js = cls.caminho_js.read_text(encoding="utf-8")

    def test_localizacao_pedida_apenas_no_clique(self) -> None:
        self.assertIn('addEventListener("click"', self.js)
        self.assertIn("getCurrentPosition", self.js)
        self.assertNotIn("getCurrentPosition()", self.js)

    def test_usa_alta_precisao(self) -> None:
        self.assertIn("enableHighAccuracy: true", self.js)

    def test_preenche_latitude_e_longitude(self) -> None:
        self.assertIn('getElementById("latitude")', self.js)
        self.assertIn('getElementById("longitude")', self.js)

    def test_trata_erros_de_localizacao(self) -> None:
        self.assertIn("function onErro", self.js)
        self.assertIn("erro.code", self.js)

    def test_impede_envio_sem_localizacao(self) -> None:
        self.assertIn('addEventListener("submit"', self.js)
        self.assertIn("preventDefault", self.js)
