from typing import Union

from django.contrib import admin, messages
from django import forms
from django.db.models.query_utils import Q
from django.http.request import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls.base import reverse_lazy
from unfold.admin import ModelAdmin, StackedInline, TabularInline
from unfold.decorators import action
# from unfold.enums import ActionVariant
from app.models import Compte, Transaction
from django.utils.translation import gettext as _


class TransactionForm(forms.Form):
    amount = forms.DecimalField(decimal_places=2, max_digits=10, min_value=0)


class TransactionsStackedInline(TabularInline):
    model = Transaction
    extra = 0
    fields = ('created_at', 'amount', 'description')
    ordering = ["-created_at"]
    readonly_fields = ('amount','description', 'created_at')
    can_delete = False

    def has_add_permission(self, request, obj):
        return False


@admin.register(Compte)
class CompteAdmin(ModelAdmin):
    list_display = ('name', 'salary', 'total', 'client', 'manager')
    search_fields = ['name']
    list_filter = ['manager', 'client']
    list_per_page = 10

    inlines = (TransactionsStackedInline, )

    actions_detail = ["add_money", "take_money", "compress_compte_transactions"]

    def get_fields(self, request, obj=None):
        fields = ['name', 'salary', 'client', 'manager']
        if obj:
            fields.append('total')
        return fields


    def get_readonly_fields(self, request, obj=None):
        if obj:  # Check if the instance already exists
            return ('client','manager', 'total')
        return ('total')



    def _display_transaction_form(self, request, form, obj):
        return render(
            request,
            "forms/transaction_form.html",
            {
                "form": form,
                "object": obj,
                "title": _("Ajouter de l'argent sur le compte {}").format(obj),
                **self.admin_site.each_context(request),
            },
        )

    @action(
        description=_("Compresser les transactions"),
        # url_path="compre-transactions-action",
        # attrs={"target": "_blank"},
    )
    def compress_compte_transactions(self, request: HttpRequest, object_id:int):
        compte = get_object_or_404(Compte, pk=object_id)
        compte.compress_transactions()
        return redirect(
            reverse_lazy("admin:app_compte_change", args=(object_id,))
        )

    @action(
        description=_("Ajouter de l'argent au compte"),
        url_path="compte-add-action",
        icon="add",
        permissions=['add_money']
    )
    def add_money(self, request: HttpRequest, object_id: int) -> str:
        # Check if object already exists, otherwise returs 404
        obj = get_object_or_404(Compte, pk=object_id)
        form = TransactionForm(request.POST or None)

        if request.method == "POST" and form.is_valid():
            # Process form data
            amount = form.cleaned_data["amount"]
            try:
                obj.add_money(amount)
            except ValueError as e:
                messages.error(request, e)
            obj.save()

            messages.success(request, _(f"Le compte a été crédité de {amount}€"))

            return redirect(
                reverse_lazy("admin:app_compte_change", args=[object_id])
            )

        return self._display_transaction_form(request, form, obj)


    @action(
        description=_("Prélever de l'argent sur le compte"),
        url_path="compte-remove-action",
        icon="remove",
        permissions=['take_money']
    )
    def take_money(self, request: HttpRequest, object_id: int) -> str:
        # Check if object already exists, otherwise returs 404
        obj = get_object_or_404(Compte, pk=object_id)
        form = TransactionForm(request.POST or None)

        if request.method == "POST" and form.is_valid():
            # Process form data
            amount = form.cleaned_data["amount"]
            try:
                obj.take_money(amount)
            except ValueError as e:
                messages.error(request, e)

            obj.save()

            messages.warning(request, _(f"Le compte a été débité de {amount}€"))

            return redirect(
                reverse_lazy("admin:app_compte_change", args=[object_id])
            )

        return self._display_transaction_form(request, form, obj)

    def has_add_money_permission(self, request: HttpRequest, object_id: Union[int, str]) -> bool:
        obj = get_object_or_404(Compte, pk=object_id)
        return request.user == obj.manager

    def has_take_money_permission(self, request: HttpRequest, object_id: Union[int, str]) -> bool:
        obj = get_object_or_404(Compte, pk=object_id)
        return request.user == obj.manager


    def get_list_filter(self, request):
        # On affiche les filtres uniquement pour le superutilisateur
        return self.list_filter if request.user.is_superuser else []

    
    def has_change_permission(self, request, obj:Compte = None):
    # Ne peut changer que si l'utilisateur est manager
        if obj is None:
             return False
        return request.user == obj.manager
    
    def has_view_permission(self, request, obj:Compte = None):
        # Ne peut visionner que si possesseur ou manager d'un compte
        if obj is None:
            return request.user.is_superuser or request.user.comptes.exists() or request.user.mon_compte.exists()
        # Ne peut voir les détails du compte que si possesseur ou manager du compte
        return request.user == obj.manager or request.user == obj.client

    def has_module_permission(self, request):
        # Permet à tout utilisateur staff ou superuser de voir le module
        return request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)

    def has_add_permission(self, request):
        # Permet à tout utilisateur staff ou superuser d'ajouter un compte
        return request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        query_set = super().get_queryset(request)
        if not request.user.is_superuser:
            query_set = query_set.filter(Q(manager=request.user) | Q(client=request.user))
        return query_set
    




@admin.register(Transaction)
class TransactionAdmin(ModelAdmin):
    list_display = ('compte', 'amount', 'description', 'created_at')
    search_fields = ['compte']
    list_filter = ['compte']
    list_per_page = 10

    def get_list_filter(self, request):
        # On affiche les filtres uniquement pour le superutilisateur
        return self.list_filter if request.user.is_superuser else []

    def get_queryset(self, request):
        query_set = super().get_queryset(request)
        if not request.user.is_superuser:
            query_set = query_set.filter(Q(compte__manager=request.user) | Q(compte__client=request.user))
        return query_set

    def has_view_permission(self, request, obj:Transaction = None):
        # Ne peut visionner que si possesseur ou manager d'un compte
        if obj is None:
            return request.user.is_superuser or request.user.comptes.exists() or request.user.mon_compte.exists()
        # Ne peut voir les détails du compte que si possesseur ou manager du compte
        return request.user == obj.compte.manager or request.user == obj.compte.client

    def has_module_permission(self, request):
        # Peut accéder au module uniquement si a un compte ou est manager d'un compte
        if not hasattr(request.user, 'comptes'):
            return False
        return request.user.is_superuser or request.user.comptes.exists() or request.user.mon_compte.exists()

    def has_delete_permission(self, request, obj=None):
        return False


    def has_change_permission(self, request, obj=None):
        # Une transaction ne peut pas être modifiée
        return False

    def has_add_permission(self, request):
        # Autorise tout utilisateur staff à créer un compte bancaire
        return request.user.is_authenticated and (request.user.is_staff or request.user.is_superuser)

