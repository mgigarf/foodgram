# Generated by Django 4.2.18 on 2025-02-03 19:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0002_alter_user_last_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'default_related_name': 'following', 'verbose_name': 'Подписчик', 'verbose_name_plural': 'Подписчики'},
        ),
    ]
