import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Ocorrencia',
            fields=[
                (
                    'id',
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name='ID',
                    ),
                ),
                (
                    'tipo',
                    models.CharField(
                        choices=[
                            ('buraco', 'Buraco na via'),
                            ('calcada', 'Calçada danificada'),
                            ('iluminacao', 'Iluminação pública'),
                            ('lixo', 'Lixo ou entulho'),
                            ('sinalizacao', 'Sinalização ou semáforo'),
                            ('arvore', 'Árvore (poda ou queda)'),
                            ('esgoto', 'Esgoto ou vazamento'),
                            ('alagamento', 'Alagamento'),
                            ('vandalismo', 'Pichação ou vandalismo'),
                            ('furto', 'Roubo ou furto'),
                            ('outros', 'Outros'),
                        ],
                        max_length=30,
                    ),
                ),
                ('descricao', models.TextField(blank=True)),
                (
                    'localizacao',
                    django.contrib.gis.db.models.fields.PointField(
                        blank=True,
                        null=True,
                        srid=4326,
                    ),
                ),
                ('criada_em', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'ocorrência',
                'verbose_name_plural': 'ocorrências',
                'ordering': ['-criada_em'],
            },
        ),
    ]
