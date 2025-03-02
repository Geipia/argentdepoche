from django.contrib import admin
from django import forms
from django.db.models.query_utils import Q
from django.http.request import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.urls.base import reverse_lazy
from unfold.admin import ModelAdmin
# from unfold.enums import ActionVariant
from unfold.decorators import action
from app.models import Compte, Transaction
from django.utils.translation import gettext as _


class TransactionForm(forms.Form):
    amount = forms.DecimalField(decimal_places=2, max_digits=10, min_value=0)


@admin.register(Compte)
class CompteAdmin(ModelAdmin):
    list_display = ('name', 'salary', 'total', 'client')
    search_fields = ['name']
    list_filter = ['manager', 'client']
    list_per_page = 10

    actions_detail = ["add_money", "take_money"]

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

    @action(description=_("Ajouter de l'argent au compte"), url_path="compte-add-action", icon="add")
    def add_money(self, request: HttpRequest, object_id: int) -> str:
        # Check if object already exists, otherwise returs 404
        obj = get_object_or_404(Compte, pk=object_id)
        form = TransactionForm(request.POST or None)

        if request.method == "POST" and form.is_valid():
            # Process form data
            amount = form.cleaned_data["amount"]

            obj.add_money(amount)
            obj.save()

            # messages.success(request, _("Change detail action has been successful."))

            return redirect(
                reverse_lazy("admin:app_compte_change", args=[object_id])
            )

        return self._display_transaction_form(request, form, obj)


    @action(description=_("Prélever de l'argent sur le compte"), url_path="compte-remove-action", icon="remove")
    def take_money(self, request: HttpRequest, object_id: int) -> str:
        # Check if object already exists, otherwise returs 404
        obj = get_object_or_404(Compte, pk=object_id)
        form = TransactionForm(request.POST or None)

        if request.method == "POST" and form.is_valid():
            # Process form data
            amount = form.cleaned_data["amount"]

            obj.take_money(amount)
            obj.save()

            # messages.success(request, _("Change detail action has been successful."))

            return redirect(
                reverse_lazy("admin:app_compte_change", args=[object_id])
            )

        return self._display_transaction_form(request, form, obj)



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
        if not request.user:
            return False
        # Peut accéder au module uniquement si a un compte ou est manager d'un compte
        if request.user.is_superuser:
            return True
        if not hasattr(request.user, 'comptes'):
            return False
        return request.user.comptes.exists() or request.user.mon_compte.exists()

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


    def has_change_permission(self, request, obj=None):
        # Une transaction ne peut pas être modifiée
        return False

