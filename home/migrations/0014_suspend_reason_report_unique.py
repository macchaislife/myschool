from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0013_report_studentid_suspended'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentid',
            name='suspend_reason',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddConstraint(
            model_name='report',
            constraint=models.UniqueConstraint(
                fields=('reporter', 'target_type', 'target_id'),
                name='unique_report_per_student_per_target',
            ),
        ),
    ]