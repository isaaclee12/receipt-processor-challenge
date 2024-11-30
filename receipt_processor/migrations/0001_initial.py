# Generated by Django 5.1 on 2024-11-30 03:32

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Item',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Receipt',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('retailer', models.CharField(max_length=30)),
                ('purchase_datetime', models.DateTimeField()),
                ('total', models.DecimalField(decimal_places=2, max_digits=20)),
            ],
        ),
        migrations.CreateModel(
            name='ReceiptInfo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('short_description', models.CharField(max_length=100)),
                ('price', models.DecimalField(decimal_places=2, max_digits=20)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='receipt_processor.item')),
                ('receipt', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='receipt_processor.receipt')),
            ],
        ),
        migrations.AddField(
            model_name='receipt',
            name='items',
            field=models.ManyToManyField(through='receipt_processor.ReceiptInfo', to='receipt_processor.item'),
        ),
    ]