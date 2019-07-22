# Generated by Django 2.0 on 2019-03-02 10:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounting', '0003_auto_20190223_1848'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='receiving_party',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='received_transactions', to='projects.Person', verbose_name='Receiving Party'),
        ),
    ]