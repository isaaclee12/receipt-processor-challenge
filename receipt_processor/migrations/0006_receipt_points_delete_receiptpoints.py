# Generated by Django 5.1 on 2024-11-30 04:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('receipt_processor', '0005_receiptpoints'),
    ]

    operations = [
        migrations.AddField(
            model_name='receipt',
            name='points',
            field=models.IntegerField(default=0),
        ),
        migrations.DeleteModel(
            name='ReceiptPoints',
        ),
    ]
