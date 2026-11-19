from django.db import models
from django.core.exceptions import ValidationError
from django.db.models import Q


class Account(models.Model):
    class AccountType(models.TextChoices):
        ASSET = "ASSET", "Asset"
        LIABILITY = "LIABILITY", "Liability"
        EQUITY = "EQUITY", "Equity"
        REVENUE = "REVENUE", "Revenue"
        EXPENSE = "EXPENSE", "Expense"

    class AccountLevel(models.IntegerChoices):
        GROUP = 1, "Group"
        LEDGER = 2, "Ledger"
        DETAIL = 3, "Detail"

    code = models.CharField(
        max_length=20,
        unique=True
    )

    name = models.CharField(
        max_length=200
    )

    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices
    )

    level = models.PositiveSmallIntegerField(
        choices=AccountLevel.choices,
        default=AccountLevel.DETAIL
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="children"
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.code} - {self.name}"


class JournalEntry(models.Model):
    date = models.DateField()

    description = models.CharField(
        max_length=500
    )

    reference = models.CharField(
        max_length=100,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.date} - {self.description}"


class JournalEntryLine(models.Model):
    journal_entry = models.ForeignKey(
        JournalEntry,
        on_delete=models.CASCADE,
        related_name="lines"
    )

    account = models.ForeignKey(
        Account,
        on_delete=models.PROTECT,
        related_name="journal_lines"
    )

    debit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    credit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    description = models.CharField(
        max_length=300,
        blank=True
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(
                    (Q(debit__gt=0) & Q(credit=0)) |
                    (Q(credit__gt=0) & Q(debit=0))
                ),
                name="line_debit_or_credit_only",
            ),
        ]

    def clean(self):
        if self.debit > 0 and self.credit > 0:
            raise ValidationError(
                "A journal line cannot have both debit and credit."
            )

        if self.debit == 0 and self.credit == 0:
            raise ValidationError(
                "A journal line must have either debit or credit."
            )

    def __str__(self):
        return f"{self.account} - {self.debit} / {self.credit}"