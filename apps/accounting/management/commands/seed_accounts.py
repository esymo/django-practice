from django.core.management.base import BaseCommand
from apps.accounting.models import Account


class Command(BaseCommand):
    help = "Create the initial chart of accounts"

    def handle(self, *args, **options):

        accounts = [
            # Assets
            {
                "code": "1000",
                "name": "دارایی‌ها",
                "type": Account.AccountType.ASSET,
                "level": Account.AccountLevel.GROUP,
            },
            {
                "code": "1100",
                "name": "دارایی‌های جاری",
                "type": Account.AccountType.ASSET,
                "level": Account.AccountLevel.LEDGER,
                "parent": "1000",
            },
            {
                "code": "1101",
                "name": "صندوق",
                "type": Account.AccountType.ASSET,
                "level": Account.AccountLevel.DETAIL,
                "parent": "1100",
            },
            {
                "code": "1102",
                "name": "بانک",
                "type": Account.AccountType.ASSET,
                "level": Account.AccountLevel.DETAIL,
                "parent": "1100",
            },
            {
                "code": "1103",
                "name": "حساب‌های دریافتنی",
                "type": Account.AccountType.ASSET,
                "level": Account.AccountLevel.DETAIL,
                "parent": "1100",
            },
            {
                "code": "1104",
                "name": "موجودی کالا",
                "type": Account.AccountType.ASSET,
                "level": Account.AccountLevel.DETAIL,
                "parent": "1100",
            },

            # Liabilities
            {
                "code": "2000",
                "name": "بدهی‌ها",
                "type": Account.AccountType.LIABILITY,
                "level": Account.AccountLevel.GROUP,
            },
            {
                "code": "2100",
                "name": "بدهی‌های جاری",
                "type": Account.AccountType.LIABILITY,
                "level": Account.AccountLevel.LEDGER,
                "parent": "2000",
            },
            {
                "code": "2101",
                "name": "حساب‌های پرداختنی",
                "type": Account.AccountType.LIABILITY,
                "level": Account.AccountLevel.DETAIL,
                "parent": "2100",
            },

            # Equity
            {
                "code": "3000",
                "name": "سرمایه",
                "type": Account.AccountType.EQUITY,
                "level": Account.AccountLevel.GROUP,
            },
            {
                "code": "3101",
                "name": "سرمایه مالک",
                "type": Account.AccountType.EQUITY,
                "level": Account.AccountLevel.DETAIL,
                "parent": "3000",
            },

            # Revenue
            {
                "code": "4000",
                "name": "درآمدها",
                "type": Account.AccountType.REVENUE,
                "level": Account.AccountLevel.GROUP,
            },
            {
                "code": "4101",
                "name": "درآمد فروش",
                "type": Account.AccountType.REVENUE,
                "level": Account.AccountLevel.DETAIL,
                "parent": "4000",
            },

            # Expenses
            {
                "code": "5000",
                "name": "هزینه‌ها",
                "type": Account.AccountType.EXPENSE,
                "level": Account.AccountLevel.GROUP,
            },
            {
                "code": "5101",
                "name": "هزینه اجاره",
                "type": Account.AccountType.EXPENSE,
                "level": Account.AccountLevel.DETAIL,
                "parent": "5000",
            },
            {
                "code": "5102",
                "name": "هزینه برق",
                "type": Account.AccountType.EXPENSE,
                "level": Account.AccountLevel.DETAIL,
                "parent": "5000",
            },
            {
                "code": "5103",
                "name": "هزینه آب",
                "type": Account.AccountType.EXPENSE,
                "level": Account.AccountLevel.DETAIL,
                "parent": "5000",
            },
            {
                "code": "5104",
                "name": "هزینه حقوق",
                "type": Account.AccountType.EXPENSE,
                "level": Account.AccountLevel.DETAIL,
                "parent": "5000",
            },
        ]

        created_count = 0

        for data in accounts:
            parent_code = data.pop("parent", None)

            parent = None

            if parent_code:
                parent = Account.objects.get(code=parent_code)

            account, created = Account.objects.get_or_create(
                code=data["code"],
                defaults={
                    "name": data["name"],
                    "account_type": data["type"],
                    "level": data["level"],
                    "parent": parent,
                },
            )

            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Created: {account.code} - {account.name}"
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. {created_count} accounts created."
            )
        )