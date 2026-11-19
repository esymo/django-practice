from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.forms import formset_factory
from django.forms import BaseFormSet


from .models import Account, JournalEntry


class JournalEntryForm(forms.ModelForm):
    class Meta:
        model = JournalEntry
        fields = [
            "date",
            "description",
            "reference",
        ]

        widgets = {
            "date": forms.DateInput(
                attrs={
                    "type": "date",
                    "class": "form-control",
                }
            ),
            "description": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "شرح سند",
                }
            ),
            "reference": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "شماره / مرجع",
                }
            ),
        }


class JournalEntryLineForm(forms.Form):
    account = forms.ModelChoiceField(
        queryset=Account.objects.filter(
            level=Account.AccountLevel.DETAIL,
            is_active=True,
        ).order_by("code"),
        label="حساب",
        widget=forms.Select(
            attrs={
                "class": "form-select",
            }
        ),
    )

    debit = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal("0"),
        required=False,
        label="بدهکار",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control debit-input",
                "min": "0",
                "step": "0.01",
                "placeholder": "0",
            }
        ),
    )

    credit = forms.DecimalField(
        max_digits=15,
        decimal_places=2,
        min_value=Decimal("0"),
        required=False,
        label="بستانکار",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control credit-input",
                "min": "0",
                "step": "0.01",
                "placeholder": "0",
            }
        ),
    )

    description = forms.CharField(
        required=False,
        label="شرح",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "شرح ردیف",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()

        account = cleaned_data.get("account")
        debit = cleaned_data.get("debit") or Decimal("0")
        credit = cleaned_data.get("credit") or Decimal("0")

        # اگر ردیف کاملاً خالی باشد،
        # Formset آن را نادیده می‌گیرد.
        if not account and debit == 0 and credit == 0:
            return cleaned_data

        if not account:
            raise ValidationError("حساب را انتخاب کنید.")

        if debit > 0 and credit > 0:
            raise ValidationError(
                "یک ردیف نمی‌تواند همزمان بدهکار و بستانکار باشد."
            )

        if debit == 0 and credit == 0:
            raise ValidationError(
                "برای ردیف حسابداری مبلغ بدهکار یا بستانکار را وارد کنید."
            )

        return cleaned_data

class BaseJournalEntryLineFormSet(BaseFormSet):

    def clean(self):
        super().clean()

        if any(self.errors):
            return

        total_debit = Decimal("0")
        total_credit = Decimal("0")
        valid_lines = 0

        for form in self.forms:
            if not form.cleaned_data:
                continue

            account = form.cleaned_data.get("account")
            debit = form.cleaned_data.get("debit") or Decimal("0")
            credit = form.cleaned_data.get("credit") or Decimal("0")

            if not account:
                continue

            valid_lines += 1
            total_debit += debit
            total_credit += credit

        if valid_lines < 2:
            raise ValidationError(
                "سند حسابداری باید حداقل دو ردیف داشته باشد."
            )

        if total_debit != total_credit:
            raise ValidationError(
                f"سند نامتوازن است. "
                f"بدهکار: {total_debit} - "
                f"بستانکار: {total_credit}"
            )

JournalEntryLineFormSet = formset_factory(
    JournalEntryLineForm,
    formset=BaseJournalEntryLineFormSet,
    extra=2,
    min_num=2,
    validate_min=True,
)
