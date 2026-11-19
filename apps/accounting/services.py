from decimal import Decimal

from django.db import transaction
from django.core.exceptions import ValidationError

from .models import Account, JournalEntry, JournalEntryLine


@transaction.atomic
def create_journal_entry(
    *,
    date,
    description,
    lines,
    reference=""
):
    """
    Create a balanced double-entry journal entry.

    lines example:

    [
        {
            "account": account,
            "debit": Decimal("1000000"),
            "credit": Decimal("0"),
        },
        {
            "account": account,
            "debit": Decimal("0"),
            "credit": Decimal("1000000"),
        },
    ]
    """

    if not lines:
        raise ValidationError("Journal entry must contain at least two lines.")

    if len(lines) < 2:
        raise ValidationError("A journal entry requires at least two lines.")

    total_debit = Decimal("0")
    total_credit = Decimal("0")

    for line in lines:
        account = line["account"]

        if account.level != Account.AccountLevel.DETAIL:
             raise ValidationError(
            f"Account {account.code} - {account.name} "
            "cannot be used directly in a journal entry."
            )

        if not account.is_active:
             raise ValidationError(
            f"Account {account.code} - {account.name} is inactive."
             )
        debit = Decimal(str(line.get("debit", 0)))
        credit = Decimal(str(line.get("credit", 0)))
        account = line["account"]

        if account.level != Account.AccountLevel.DETAIL:
            raise ValidationError(
                f"Account {account.code} - {account.name} "
                 "cannot be used directly in a journal entry."
            )
        if debit < 0 or credit < 0:
            raise ValidationError(
                "Debit and credit amounts cannot be negative."
            )

        if debit > 0 and credit > 0:
            raise ValidationError(
                "A journal line cannot have both debit and credit."
            )

        if debit == 0 and credit == 0:
            raise ValidationError(
                "A journal line must have either debit or credit."
            )

        total_debit += debit
        total_credit += credit

    if total_debit != total_credit:
        raise ValidationError(
            f"Journal entry is not balanced. "
            f"Debit: {total_debit}, Credit: {total_credit}"
        )

    entry = JournalEntry.objects.create(
        date=date,
        description=description,
        reference=reference
    )

    for line in lines:
        JournalEntryLine.objects.create(
            journal_entry=entry,
            account=line["account"],
            debit=Decimal(str(line.get("debit", 0))),
            credit=Decimal(str(line.get("credit", 0))),
            description=line.get("description", "")
        )

    return entry