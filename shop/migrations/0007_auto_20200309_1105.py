# Generated by Django 2.2.9 on 2020-03-09 11:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0006_auto_20200226_0914'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveryaddress',
            name='uuid',
            field=models.UUIDField(default=5056363248130, editable=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='uuid',
            field=models.UUIDField(default=121465736436712, editable=False),
        ),
        migrations.AlterField(
            model_name='product',
            name='uuid',
            field=models.UUIDField(default=116248565956469, editable=False),
        ),
        migrations.AlterField(
            model_name='review',
            name='uuid',
            field=models.UUIDField(default=139284296762677, editable=False),
        ),
    ]
