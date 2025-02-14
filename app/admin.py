from django.contrib import admin
from django.db.models.query_utils import Q

from app.models import Compte, Transaction

@admin.register(Compte)
class CompteAdmin(admin.ModelAdmin):
    list_display = ('name', 'salary', 'total', 'client')
    search_fields = ['name']
    list_filter = ['manager', 'client']
    list_per_page = 10

    def get_list_filter(self, request):
        # On affiche les filtres uniquement pour le superutilisateur
        return self.list_filter if request.user.is_superuser else []

    
    # def has_change_permission(self, request, obj:Compte = None):
    #     # Ne peut changer que si l'utilisateur est manager
    #     if obj is None:
    #         return False
    #     return super
    
    def has_view_permission(self, request, obj:Compte = None):
        # Ne peut visionner que si possesseur ou manager d'un compte
        if obj is None:
            return request.user.is_superuser or request.user.comptes.exists() or request.user.mon_compte.exists()
        # Ne peut voir les détails du compte que si possesseur ou manager du compte
        return request.user == obj.manager or request.user == obj.client

    def has_module_permission(self, request):
        # Peut accéder au module uniquement si a un compte ou est manager d'un compte
        return request.user.is_superuser or request.user.comptes.exists() or request.user.mon_compte.exists()

    def get_queryset(self, request):
        query_set = super().get_queryset(request)
        if not request.user.is_superuser:
            query_set = query_set.filter(Q(manager=request.user) | Q(client=request.user))
        return query_set



@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
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
        return request.user.is_superuser or request.user.comptes.exists() or request.user.mon_compte.exists()


    def has_change_permission(self, request, obj=None):
        # Une transaction ne peut pas être modifiée
        return False

