# Generated by Django 4.2.5 on 2024-01-11 16:47

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("enedis", "0002_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sgetiersdevice",
            name="auto_create_variables",
            field=models.ManyToManyField(blank=True, to="enedis.sgetiersfield"),
        ),
        migrations.AlterField(
            model_name="sgetiersdevice",
            name="certificat",
            field=models.FilePathField(
                blank=True, max_length=254, path="/home/pyscada/enedisCertificates"
            ),
        ),
        migrations.AlterField(
            model_name="sgetiersdevice",
            name="login",
            field=models.EmailField(blank=True, max_length=254),
        ),
        migrations.AlterField(
            model_name="sgetiersdevice",
            name="pdl",
            field=models.PositiveBigIntegerField(blank=True),
        ),
        migrations.AlterField(
            model_name="sgetiersdevice",
            name="private_key",
            field=models.FilePathField(
                blank=True, max_length=254, path="/home/pyscada/enedisCertificates"
            ),
        ),
    ]