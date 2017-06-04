# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-05-23 15:25
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Items',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, verbose_name='商品名')),
                ('price', models.IntegerField(blank=True, default=0, verbose_name='値段')),
                ('category', models.IntegerField(default=0, verbose_name='カテゴリ')),
                ('created_at', models.DateField(default=datetime.date.today, verbose_name='作成日')),
                ('updated_at', models.DateField(default=datetime.date.today, verbose_name='更新日')),
            ],
        ),
        migrations.CreateModel(
            name='Purchases',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recommend.Items')),
            ],
        ),
        migrations.CreateModel(
            name='Users',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, verbose_name='名前')),
                ('age', models.IntegerField(blank=True, default=0, verbose_name='年齢')),
                ('sex', models.CharField(blank=True, default='', max_length=2, verbose_name='性別')),
            ],
        ),
        migrations.AddField(
            model_name='purchases',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='recommend.Users'),
        ),
    ]