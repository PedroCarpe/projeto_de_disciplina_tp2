from django.test import SimpleTestCase, TestCase
from django.contrib.auth.models import User

from ocorrencias.forms import OcorrenciaForm
from ocorrencias.models import Ocorrencia


class OcorrenciaFormUnitTests(SimpleTestCase):
    def test_formulario_valida_dados_corretos_sem_salvar(self) -> None:
        formulario = OcorrenciaForm(
            {
                "tipo": "buraco",
                "descricao": "Buraco na calçada",
                "latitude": "-23.550500",
                "longitude": "-46.633300",
            }
        )

        self.assertTrue(formulario.is_valid())
        self.assertEqual(formulario.cleaned_data["tipo"], "buraco")
        self.assertEqual(formulario.cleaned_data["descricao"], "Buraco na calçada")
        self.assertEqual(str(formulario.cleaned_data["latitude"]), "-23.550500")
        self.assertEqual(str(formulario.cleaned_data["longitude"]), "-46.633300")


class OcorrenciaFormSaveTests(TestCase):
    def setUp(self) -> None:
        self.usuario = User.objects.create_user(
            username="ana@exemplo.com",
            email="ana@exemplo.com",
            password="senhaSegura123",
        )

    def test_save_cria_ocorrencia_com_localizacao(self) -> None:
        formulario = OcorrenciaForm(
            {
                "tipo": "buraco",
                "descricao": "Buraco na calçada",
                "latitude": "-23.550500",
                "longitude": "-46.633300",
            }
        )

        self.assertTrue(formulario.is_valid())

        ocorrencia = formulario.save(self.usuario)

        self.assertIsNotNone(ocorrencia.pk)
        self.assertEqual(Ocorrencia.objects.count(), 1)
        self.assertEqual(ocorrencia.usuario, self.usuario)
        self.assertEqual(ocorrencia.tipo, "buraco")
        self.assertAlmostEqual(ocorrencia.localizacao.x, -46.6333)
        self.assertAlmostEqual(ocorrencia.localizacao.y, -23.5505)
