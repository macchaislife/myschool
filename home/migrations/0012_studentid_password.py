# Generated manually to add student login password support

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0011_opinioncomment'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentid',
            name='password',
            field=models.CharField(blank=True, max_length=128),
        ),
        migrations.AddField(
            model_name='studentid',
            name='must_change_password',
            field=models.BooleanField(default=True),
        ),
    ]