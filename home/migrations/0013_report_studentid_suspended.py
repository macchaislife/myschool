from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0012_studentid_password'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentid',
            name='suspended_until',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('target_type', models.CharField(choices=[('opinion', '意見'), ('comment', 'コメント'), ('lesson_question', '授業への質問')], max_length=20)),
                ('target_id', models.PositiveIntegerField()),
                ('reason', models.CharField(choices=[('troll', '荒らし・嫌がらせ'), ('abuse', '誹謗中傷'), ('spam', 'スパム・宣伝'), ('other', 'その他')], default='other', max_length=20)),
                ('detail', models.TextField(blank=True)),
                ('status', models.CharField(choices=[('pending', '未対応'), ('reviewed', '対応済み')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('reported_student', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports_received', to='home.studentid')),
                ('reporter', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='reports_filed', to='home.studentid')),
            ],
        ),
    ]