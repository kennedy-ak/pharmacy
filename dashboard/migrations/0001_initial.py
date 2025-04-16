# Generated by Django 5.2 on 2025-04-11 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DailySummary',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(unique=True)),
                ('total_sales', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('total_purchases', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('profit', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('items_sold', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'Daily Summaries',
            },
        ),
        migrations.CreateModel(
            name='StockAlert',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('drug_name', models.CharField(max_length=100)),
                ('alert_type', models.CharField(choices=[('low_stock', 'Low Stock'), ('expiry', 'Expiry Alert')], max_length=20)),
                ('message', models.TextField()),
                ('is_resolved', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('resolved_at', models.DateTimeField(blank=True, null=True)),
            ],
        ),
    ]
