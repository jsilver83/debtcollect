# Generated by Django 2.0 on 2019-07-22 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('insurancedebt', '0009_insurancedebt_ref_no'),
    ]

    operations = [
        migrations.AddField(
            model_name='scheduledpayment',
            name='proof_of_payment',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='Proof Of Payment'),
        ),
    ]
