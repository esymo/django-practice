from django.contrib import messages
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from decimal import Decimal
from django.db.models import Q, Sum

from .forms import JournalEntryForm, JournalEntryLineFormSet
from .models import Account, JournalEntry, JournalEntryLine
from .services import create_journal_entry


def journal_entry_create(request):
    if request.method == "POST":
        entry_form = JournalEntryForm(request.POST)
        line_formset = JournalEntryLineFormSet(request.POST)

        if entry_form.is_valid() and line_formset.is_valid():
            lines = []

            for form in line_formset:
                cleaned = form.cleaned_data

                if not cleaned:
                    continue

                account = cleaned.get("account")
                debit = cleaned.get("debit") or 0
                credit = cleaned.get("credit") or 0
                description = cleaned.get("description", "")

                if not account:
                    continue

                lines.append(
                    {
                        "account": account,
                        "debit": debit,
                        "credit": credit,
                        "description": description,
                    }
                )

            try:
                create_journal_entry(
                    date=entry_form.cleaned_data["date"],
                    description=entry_form.cleaned_data["description"],
                    reference=entry_form.cleaned_data["reference"],
                    lines=lines,
                )

                messages.success(
                    request,
                    "سند حسابداری با موفقیت ثبت شد."
                )

                return redirect("journal_entry_create")

            except ValidationError as error:
                entry_form.add_error(None, error)

    else:
        entry_form = JournalEntryForm()
        line_formset = JournalEntryLineFormSet()

    return render(
        request,
        "accounting/journal_entry_form.html",
        {
            "entry_form": entry_form,
            "line_formset": line_formset,
        },
    )


def journal_entry_list(request):
    entries = (
        JournalEntry.objects
        .prefetch_related("lines")
        .order_by("-date", "-id")
    )

    for entry in entries:
        totals = entry.lines.aggregate(
            total_debit=Sum("debit"),
            total_credit=Sum("credit"),
        )

        entry.total_debit = totals["total_debit"] or 0
        entry.total_credit = totals["total_credit"] or 0

    return render(
        request,
        "accounting/journal_entry_list.html",
        {
            "entries": entries,
        },
    )


def journal_entry_detail(request, pk):
    entry = get_object_or_404(
        JournalEntry.objects.prefetch_related(
            "lines__account"
        ),
        pk=pk,
    )

    totals = entry.lines.aggregate(
        total_debit=Sum("debit"),
        total_credit=Sum("credit"),
    )

    total_debit = totals["total_debit"] or 0
    total_credit = totals["total_credit"] or 0

    return render(
        request,
        "accounting/journal_entry_detail.html",
        {
            "entry": entry,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "is_balanced": total_debit == total_credit,
        },
    )
def account_ledger(request, pk):
    account = get_object_or_404(
        Account,
        pk=pk,
    )

    lines = (
        JournalEntryLine.objects
        .select_related("journal_entry", "account")
        .filter(account=account)
        .order_by(
            "journal_entry__date",
            "journal_entry__id",
            "id",
        )
    )

    totals = lines.aggregate(
        total_debit=Sum("debit"),
        total_credit=Sum("credit"),
    )

    total_debit = totals["total_debit"] or Decimal("0")
    total_credit = totals["total_credit"] or Decimal("0")

    balance = Decimal("0")

    for line in lines:
        balance += line.debit
        balance -= line.credit
        line.balance = balance

    return render(
        request,
        "accounting/account_ledger.html",
        {
            "account": account,
            "lines": lines,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "balance": balance,
        },
    )
def account_list(request):
    accounts = (
        Account.objects
        .select_related("parent")
        .prefetch_related("children")
        .order_by("code")
    )

    return render(
        request,
        "accounting/account_list.html",
        {
            "accounts": accounts,
        },
    )
def trial_balance(request):
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    lines_filter = {}

    if from_date:
        lines_filter["journal_entry__date__gte"] = from_date

    if to_date:
        lines_filter["journal_entry__date__lte"] = to_date

    accounts = (
        Account.objects
        .filter(
            level=Account.AccountLevel.DETAIL,
            is_active=True,
        )
        .annotate(
            total_debit=Sum(
                "journal_lines__debit",
                filter=Q(**lines_filter),
            ),
            total_credit=Sum(
                "journal_lines__credit",
                filter=Q(**lines_filter),
            ),
        )
        .order_by("code")
    )

    total_debit = Decimal("0")
    total_credit = Decimal("0")
    total_balance_debit = Decimal("0")
    total_balance_credit = Decimal("0")

    for account in accounts:

        account.total_debit = (
            account.total_debit or Decimal("0")
        )

        account.total_credit = (
            account.total_credit or Decimal("0")
        )

        net_balance = (
            account.total_debit -
            account.total_credit
        )

        if net_balance >= 0:
            account.balance_debit = net_balance
            account.balance_credit = Decimal("0")
        else:
            account.balance_debit = Decimal("0")
            account.balance_credit = abs(net_balance)

        total_debit += account.total_debit
        total_credit += account.total_credit

        total_balance_debit += account.balance_debit
        total_balance_credit += account.balance_credit

    return render(
        request,
        "accounting/trial_balance.html",
        {
            "accounts": accounts,
            "total_debit": total_debit,
            "total_credit": total_credit,
            "total_balance_debit": total_balance_debit,
            "total_balance_credit": total_balance_credit,
            "is_balanced": total_debit == total_credit,
            "from_date": from_date,
            "to_date": to_date,
        },
    )