from django.db import models
from django.contrib.auth.models import User

class Compte(models.Model):
    # protected $fillable = ['user_id', 'manager_id', 'name', 'salary', 'total'];
    name = models.CharField(max_length=24)
    salary = models.FloatField(default=0)
    #total = models.FloatField(default=0)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comptes')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mon_compte')
    
    @property
    def total (self):
        return self.transactions.aggregate(models.Sum('amount'))['amount__sum'] 

    def __str__(self):
        return self.name
    

class Transaction(models.Model):
    # protected $fillable = ['compte_id', 'amount', 'type', 'description'];
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='transactions')
    amount = models.FloatField()
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.compte.name} - {self.amount}"

# Create your models here.