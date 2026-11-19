from django.urls import path

from . import views


urlpatterns = [
    path(
        "journal-entries/",
        views.journal_entry_list,
        name="journal_entry_list",
    ),

    path(
        "journal-entries/create/",
        views.journal_entry_create,
        name="journal_entry_create",
    ),

    path(
        "journal-entries/<int:pk>/",
        views.journal_entry_detail,
        name="journal_entry_detail",
    ),
    path(
    "accounts/<int:pk>/ledger/",
    views.account_ledger,
    name="account_ledger",
    ),
    path(
    "accounts/",
    views.account_list,
    name="account_list",
    ),
    path(
    "reports/trial-balance/",
    views.trial_balance,
    name="trial_balance",
    ),
]