"""
既存の生徒（password が未設定のまま）に、ランダムな初期パスワードを
まとめて発行するための管理コマンド。

使い方:
    python manage.py generate_student_passwords

生成されたパスワードは標準出力に一度だけ表示される（DBには平文で残らない）。
必ず出力をコピーするか、リダイレクトしてファイルに保存すること。
    python manage.py generate_student_passwords > initial_passwords.csv
"""

from django.core.management.base import BaseCommand

from home.models import StudentID, generate_initial_password


class Command(BaseCommand):
    help = "password が未設定の生徒に、ランダムな初期パスワードを発行する"

    def handle(self, *args, **options):
        targets = list(StudentID.objects.filter(password=""))

        if not targets:
            self.stdout.write("対象の生徒はいません（全員パスワード設定済みです）。")
            return

        self.stdout.write("student_id,password")

        for student in targets:
            raw = generate_initial_password()
            student.set_password(raw)
            student.must_change_password = True
            student.save()
            self.stdout.write(f"{student.student_id},{raw}")

        self.stderr.write(
            self.style.WARNING(
                f"{len(targets)}件の初期パスワードを発行しました。"
                "この出力はコピーしたら安全に破棄してください。"
            )
        )