# Generated by Django 3.2 on 2023-05-30 15:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ecomapp', '0010_auto_20230405_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='payment_method',
            field=models.CharField(choices=[('Cash On Delivery', 'Cash On Delivery'), ('Paytm', 'Paytm')], default='Cash On Delivery', max_length=20),
        ),
    ]
