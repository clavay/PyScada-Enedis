# Generated by Django 4.2.5 on 2023-12-19 11:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("pyscada", "0107_alter_calculatedvariableselector_period_fields"),
        ("enedis", "0001_add_device_protocol"),
    ]

    operations = [
        migrations.CreateModel(
            name="SGETiersVariable",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "command_service_type",
                    models.CharField(
                        choices=[
                            ("technical", "Donnnées techniques contractuelles"),
                            ("detailsV3", "Mesures détaillées"),
                        ],
                        max_length=250,
                    ),
                ),
                ("xml_path", models.TextField()),
                ("found_in_last_request", models.BooleanField(default=False)),
                (
                    "sgetiers_variable",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="pyscada.variable",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SGETiersField",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("label", models.CharField(max_length=254)),
                ("xml_path", models.TextField()),
                (
                    "command_service_type",
                    models.CharField(
                        choices=[
                            ("technical", "Donnnées techniques contractuelles"),
                            ("detailsV3", "Mesures détaillées"),
                        ],
                        max_length=250,
                    ),
                ),
                ("unit", models.ForeignKey(on_delete=models.SET(1), to="pyscada.unit")),
            ],
        ),
        migrations.CreateModel(
            name="SGETiersDevice",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("login", models.EmailField(max_length=254)),
                (
                    "certificat",
                    models.FilePathField(
                        max_length=254, path="/home/pyscada/enedisCertificates"
                    ),
                ),
                (
                    "private_key",
                    models.FilePathField(
                        max_length=254, path="/home/pyscada/enedisCertificates"
                    ),
                ),
                ("pdl", models.PositiveBigIntegerField()),
                ("authorization", models.BooleanField(default=False)),
                ("initialized", models.BooleanField(default=False)),
                (
                    "auto_create_variables",
                    models.ManyToManyField(to="enedis.sgetiersfield"),
                ),
                (
                    "sgetiers_device",
                    models.OneToOneField(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="pyscada.device",
                    ),
                ),
            ],
        ),
    ]
