import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def exigir_proprietario_para_registros_existentes(apps, schema_editor):
    ocorrencia = apps.get_model('ocorrencias', 'Ocorrencia')
    if ocorrencia.objects.using(schema_editor.connection.alias).filter(
        usuario__isnull=True
    ).exists():
        raise RuntimeError(
            'Existem ocorrências sem usuário. Atribua cada registro a um usuário '
            'antes de aplicar esta migração.'
        )


class Migration(migrations.Migration):
    dependencies = [
        ('ocorrencias', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='ocorrencia',
            name='usuario',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name='ocorrencias',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(
            exigir_proprietario_para_registros_existentes,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='ocorrencia',
            name='usuario',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name='ocorrencias',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
