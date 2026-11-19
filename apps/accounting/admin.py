from django.contrib import admin
from .models import Account, JournalEntry, JournalEntryLine


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "account_type",
        "level",
        "parent",
        "is_active",
    )

    list_filter = (
        "account_type",
        "level",
        "is_active",
    )

    search_fields = (
        "code",
        "name",
    )

    ordering = ("code",)


class JournalEntryLineInline(admin.TabularInline):
    model = JournalEntryLine
    extra = 2


@admin.register(JournalEntry)
class JournalEntryAdmin(admin.ModelAdmin):
    list_display = (
        "date",
        "description",
        "reference",
        "created_at",
    )

    search_fields = (
        "description",
        "reference",
    )

    list_filter = (
        "date",
    )

    inlines = [
        JournalEntryLineInline
    ]
