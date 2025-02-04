from django.contrib import admin

from app.models import Compte, Transaction

@admin.register(Compte)
class CompteAdmin(admin.ModelAdmin):
    list_display = ('name', 'salary', 'total')
    search_fields = ['name']
    list_filter = ['manager', 'client']
    list_per_page = 10

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('compte', 'amount', 'description', 'created_at')
    search_fields = ['compte']
    list_filter = ['compte']
    list_per_page = 10

# Register your models here.
