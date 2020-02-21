# Generated by Django 2.2.9 on 2020-02-20 12:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0009_auto_20200220_1208'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveryaddress',
            name='uuid',
            field=models.UUIDField(default=39912591129335, editable=False),
        ),
        migrations.RemoveField(
            model_name='order',
            name='product',
        ),
        migrations.AddField(
            model_name='order',
            name='product',
            field=models.ManyToManyField(blank=True, null=True, related_name='order_product', to='shop.Product'),
        ),
        migrations.AlterField(
            model_name='order',
            name='uuid',
            field=models.UUIDField(default=110833203984507, editable=False),
        ),
        migrations.AlterField(
            model_name='orderline',
            name='uuid',
            field=models.UUIDField(default=20950272551602, editable=False),
        ),
        migrations.AlterField(
            model_name='product',
            name='uuid',
            field=models.UUIDField(default=125554295947961, editable=False),
        ),
        migrations.AlterField(
            model_name='review',
            name='uuid',
            field=models.UUIDField(default=109060052399511, editable=False),
        ),
    ]
