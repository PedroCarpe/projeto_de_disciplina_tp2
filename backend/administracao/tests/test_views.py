import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from django.contrib.auth.models import User
from django.test import SimpleTestCase, TestCase
from django.urls import reverse


class PainelAcessoTests(TestCase):
    def test_anonimo_e_encaminhado_para_login_com_next(self) -> None:
        resposta = self.client.get(reverse("administracao:painel"))

        self.assertEqual(resposta.status_code, 302)
        destino = urlparse(resposta.url)
        self.assertEqual(destino.path, reverse("login"))
        self.assertEqual(
            parse_qs(destino.query).get("next"), [reverse("administracao:painel")]
        )

    def test_usuario_comum_recebe_403(self) -> None:
        usuario = User.objects.create_user(
            username="comum@exemplo.com",
            email="comum@exemplo.com",
            password="senha123",
        )
        self.client.force_login(usuario)

        resposta = self.client.get(reverse("administracao:painel"))

        self.assertEqual(resposta.status_code, 403)
        self.assertContains(resposta, "Acesso restrito", status_code=403)

    def test_usuario_staff_ve_painel(self) -> None:
        usuario = User.objects.create_user(
            username="gestor@exemplo.com",
            email="gestor@exemplo.com",
            password="senha123",
            is_staff=True,
        )
        self.client.force_login(usuario)

        resposta = self.client.get(reverse("administracao:painel"))

        self.assertEqual(resposta.status_code, 200)
        self.assertTemplateUsed(resposta, "base.html")
        self.assertTemplateUsed(resposta, "administracao/painel.html")
        self.assertContains(resposta, "Administração")

    def test_admin_nativo_continua_disponivel(self) -> None:
        resposta = self.client.get(reverse("admin:index"))

        self.assertEqual(resposta.status_code, 302)
        self.assertIn(reverse("admin:login"), resposta.url)


class PainelEstruturaTests(TestCase):
    def setUp(self) -> None:
        usuario = User.objects.create_user(
            username="gestor@exemplo.com",
            email="gestor@exemplo.com",
            password="senha123",
            is_staff=True,
        )
        self.client.force_login(usuario)
        self.resposta = self.client.get(reverse("administracao:painel"))
        self.html = self.resposta.content.decode()

    def test_painel_tem_quatro_abas_acessiveis(self) -> None:
        self.assertIn('role="tablist"', self.html)

        for aba in ("relatorios", "configuracoes", "ocorrencias", "usuarios"):
            with self.subTest(aba=aba):
                self.assertIn(f'data-admin-aba="{aba}"', self.html)
                self.assertIn(f'aria-controls="painel-{aba}"', self.html)
                self.assertIn(f'id="aba-{aba}"', self.html)

        self.assertRegex(
            self.html,
            r'data-admin-aba="relatorios"[^>]*aria-selected="true"',
        )
        for aba in ("configuracoes", "ocorrencias", "usuarios"):
            with self.subTest(aba=aba):
                self.assertRegex(
                    self.html,
                    rf'data-admin-aba="{aba}"[^>]*aria-selected="false"',
                )

    def test_painel_renderiza_includes_das_quatro_abas(self) -> None:
        for aba in ("relatorios", "configuracoes", "ocorrencias", "usuarios"):
            with self.subTest(aba=aba):
                self.assertTemplateUsed(
                    self.resposta, f"administracao/includes/{aba}.html"
                )
                self.assertIn(f'id="painel-{aba}"', self.html)
                self.assertIn(f'data-admin-painel="{aba}"', self.html)

    def test_apenas_aba_inicial_visivel(self) -> None:
        self.assertNotRegex(
            self.html, r'id="painel-relatorios"[^>]*\bhidden\b'
        )
        for aba in ("configuracoes", "ocorrencias", "usuarios"):
            with self.subTest(aba=aba):
                self.assertRegex(self.html, rf'id="painel-{aba}"[^>]*\bhidden\b')

    def test_painel_reaproveita_logo_e_carrega_script_das_abas(self) -> None:
        self.assertTemplateUsed(self.resposta, "includes/logo.html")
        self.assertContains(self.resposta, "Nossa Rua.")
        self.assertContains(self.resposta, "static/js/admin.js")
        self.assertContains(self.resposta, "defer")
        self.assertNotContains(self.resposta, "leaflet")

    def test_painel_usa_texto_neutro_de_produto(self) -> None:
        self.assertContains(
            self.resposta,
            "Relatórios, configurações, ocorrências e usuários em um único lugar.",
        )
        self.assertNotContains(self.resposta, "integrações pendentes")
        self.assertNotContains(self.resposta, 'href="#"')

    def test_painel_nao_expõe_detalhes_de_desenvolvimento(self) -> None:
        for trecho in (
            "Integração pendente",
            "integrações pendentes",
            "integração com o backend",
            "Aguardando integração",
            "prévia da interface",
            "será integrado",
            "serão integradas",
        ):
            with self.subTest(trecho=trecho):
                self.assertNotContains(self.resposta, trecho)

    def test_painel_oferece_voltar_ao_inicio_e_saida(self) -> None:
        self.assertContains(self.resposta, f'href="{reverse("inicio")}"')
        self.assertContains(self.resposta, "Voltar ao início")
        self.assertContains(self.resposta, "Sair")


class ConteudoDasAbasTests(TestCase):
    def setUp(self) -> None:
        usuario = User.objects.create_user(
            username="gestor@exemplo.com",
            email="gestor@exemplo.com",
            password="senha123",
            is_staff=True,
        )
        self.client.force_login(usuario)
        self.resposta = self.client.get(reverse("administracao:painel"))
        self.html = self.resposta.content.decode()

    def test_relatorios_traz_uso_do_sistema_sem_numeros_ficticios(self) -> None:
        for trecho in (
            "Relatórios de uso do sistema",
            "Acessos",
            "Ocorrências registradas",
            "Usuários ativos",
            "Sem dados",
            "Nenhum relatório disponível ainda.",
        ):
            with self.subTest(trecho=trecho):
                self.assertContains(self.resposta, trecho)
        self.assertContains(self.resposta, "Exportar relatório")
        self.assertContains(self.resposta, "disabled")
        self.assertNotContains(self.resposta, "Aguardando integração")

    def test_configuracoes_sao_explicitamente_indisponiveis(self) -> None:
        for trecho in (
            "Nome da cidade",
            "Região padrão do mapa",
            "Tipos de ocorrência",
            "Notificações por e-mail",
            "Nenhuma alteração pode ser feita nesta tela.",
        ):
            with self.subTest(trecho=trecho):
                self.assertContains(self.resposta, trecho)
        self.assertNotContains(self.resposta, "integração com o backend")
        self.assertNotRegex(
            self.html, r'id="painel-configuracoes"[^>]*>\s*<form'
        )
        self.assertContains(self.resposta, "Salvar alterações")

    def test_ocorrencias_usam_status_e_estado_vazio(self) -> None:
        for status in ("Pendente", "Em andamento", "Resolvida"):
            with self.subTest(status=status):
                self.assertContains(self.resposta, status)
        self.assertContains(self.resposta, "Nenhuma ocorrência para exibir.")
        self.assertContains(
            self.resposta, "As ocorrências registradas aparecerão aqui."
        )
        self.assertContains(self.resposta, "Atualizar status")
        self.assertNotContains(self.resposta, "integração com o backend")
        self.assertNotContains(self.resposta, "Aberto")

    def test_usuarios_nao_simula_bloqueio(self) -> None:
        self.assertContains(
            self.resposta, "Nenhum usuário disponível para administração."
        )
        self.assertContains(self.resposta, "As contas cadastradas aparecerão aqui.")
        self.assertContains(self.resposta, "Nenhuma conta é alterada nesta tela.")
        self.assertContains(self.resposta, "Bloquear usuário")
        self.assertNotContains(self.resposta, "será integrado pelo backend")
        painel_usuarios = re.search(
            r'id="painel-usuarios".*?</section>', self.html, re.DOTALL
        )
        self.assertIsNotNone(painel_usuarios)
        self.assertNotIn("action=", painel_usuarios.group(0))


class AdminJsTests(SimpleTestCase):
    caminho_js = Path(__file__).resolve().parents[2] / "static" / "js" / "admin.js"

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.js = cls.caminho_js.read_text(encoding="utf-8")

    def test_troca_de_abas_usa_estado_aria(self) -> None:
        for trecho in (
            "data-admin-aba",
            'role="tab"',
            "aria-selected",
            "hidden",
            "tabIndex",
            "addEventListener(\"click\"",
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
