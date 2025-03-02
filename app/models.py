from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

class Compte(models.Model):
    # protected $fillable = ['user_id', 'manager_id', 'name', 'salary', 'total'];
    name = models.CharField(max_length=24, verbose_name=_('Name'))
    salary = models.FloatField(default=0, verbose_name=_('Salary'))
    #total = models.FloatField(default=0)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comptes', verbose_name=_('Manager'))
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mon_compte', verbose_name=_('Account user'))
    
    @property
    def total (self):
        return self.transactions.aggregate(models.Sum('amount'))['amount__sum'] or 0


    def add_money(self, amount:float, description:str=None):
        """
        Permet d'ajouter de l'argent à un compte

        Parameters
        ----------
        amount: float
        description
        """
        if amount < 0:
            raise ValueError('Amount cannot be negative')
        self.transactions.create(amount=amount, description=description)


    def take_money(self, amount:float, description:str=None):
        if amount < 0:
            raise ValueError('Le montant ne peut pas être négatif')
        if amount > self.total:
            raise ValueError('Vous ne pouvez pas prélever plus que le total du compte')
        self.transactions.create(amount=-amount, description=description)


    def compress_transactions(self, last_day:datetime.date = None):
        if last_day is None:
            last_day = datetime.today()
        transactions = self.transactions.filter(created_at__lte=last_day)
        compressed_transactions = Transaction(compte_id=self.id, created_at=last_day, description=f"Situation au {last_day.strftime('%d/%m/%Y')}", amount=0)
        for transaction in transactions:
            compressed_transactions.amount += transaction.amount
            transaction.delete(keep_parents=True)
        compressed_transactions.save()

    def __str__(self):
        return self.name


class Transaction(models.Model):
    # protected $fillable = ['compte_id', 'amount', 'type', 'description'];
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='transactions', verbose_name=_('Account'))
    amount = models.FloatField(verbose_name=_('Amount'))
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))


    def __str__(self):
        return f"{self.compte.name} - {self.amount}"



# Create your models here.