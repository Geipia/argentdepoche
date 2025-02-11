from django.contrib import admin

from app.models import Compte, Transaction

@admin.register(Compte)
class CompteAdmin(admin.ModelAdmin):
    list_display = ('name', 'salary', 'total')
    search_fields = ['name']
    list_filter = ['manager', 'client']
    list_per_page = 10
    
    def has_add_permission(self, request):
        return super().has_add_permission(request)
    
    def has_change_permission(self, request, obj:Compte = None):
        print(request.user, obj)
        if obj is None:
            return False
        return request.user.is_superuser or request.user == obj.manager
    
    def has_view_permission(self, request, obj:Compte = None):
        print(request.user, obj)
        if obj is None:
            return True
        return request.user.is_superuser or request.user == obj.manager or request.user == obj.client
    
    def has_module_permission(self, request):
        return True
    
    def get_queryset(self, request):
        return super().get_queryset(request).filter(manager=request.user)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('compte', 'amount', 'description', 'created_at')
    search_fields = ['compte']
    list_filter = ['compte']
    list_per_page = 10

