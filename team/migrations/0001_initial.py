# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2017-11-26 19:56
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nom')),
                ('fullname', models.CharField(max_length=100, verbose_name='Nom complet')),
                ('shortname', models.CharField(max_length=10, verbose_name='Abréviation')),
                ('is_active', models.BooleanField(default=True, verbose_name='Actif?')),
            ],
            options={
                'verbose_name': 'Equipe',
                'verbose_name_plural': 'Equipes',
                'db_table': 'team',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='TeamMember',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('member_type', models.IntegerField(default=0, verbose_name="Type d'utilisateur")),
                ('send_on_validation', models.BooleanField(default=False, verbose_name='Email quand commande validée ?')),
                ('send_on_edit', models.BooleanField(default=True, verbose_name='Email quand commande supprimée ?')),
                ('send_on_sent', models.BooleanField(default=False, verbose_name='Email quand commande envoyée ?')),
                ('team', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='team.Team', verbose_name='Equipe')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Utilisateur')),
            ],
            options={
                'verbose_name': 'Membre équipe',
                'verbose_name_plural': 'Membres équipe',
                'db_table': 'team_member',
                'ordering': ('team', 'user__username'),
            },
        ),
        migrations.CreateModel(
            name='TeamNameHistory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nom')),
                ('fullname', models.CharField(max_length=100, verbose_name='Nom')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='team.Team')),
            ],
            options={
                'verbose_name': "Historique nom d'équipe",
                'verbose_name_plural': "Historique nom d'équipe",
                'db_table': 'team_name_history',
                'ordering': ('team', 'name'),
            },
        ),
    ]