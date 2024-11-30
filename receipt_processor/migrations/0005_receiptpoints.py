# Generated by Django 5.1 on 2024-11-30 04:19

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipt_processor', '0004_alter_receipt_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='ReceiptPoints',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.IntegerField()),
                ('receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='receipt_processor.receipt')),
            ],
        ),
    ]
