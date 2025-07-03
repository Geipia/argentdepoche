from datetime import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext as _

class Compte(models.Model):
    # protected $fillable = ['user_id', 'manager_id', 'name', 'salary', 'total'];
    name = models.CharField(max_length=24, verbose_name=_('Name'), help_text=_('Nom du compte (ex: Prénom de l’enfant)'))
    salary = models.FloatField(default=0, verbose_name=_('Salary'), help_text=_('Montant du salaire hebdomadaire automatique.'))
    #total = models.FloatField(default=0)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comptes', verbose_name=_('Manager'), help_text=_('Parent ou responsable du compte.'))
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mon_compte', verbose_name=_('Account user'), help_text=_('Enfant ou bénéficiaire du compte.'))
    last_salary_payment = models.DateTimeField(null=True, blank=True, verbose_name=_('Last salary payment'), help_text=_('Date du dernier versement automatique du salaire.'))
    
    @property
    def total (self):
        return self.transactions.get_total_amount()


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
        # on récupère les transactions plus vieilles que last_day
        transactions = self.transactions.filter(created_at__lte=last_day)
        # On créé une nouvelle transaction avec le montant total de ces transactions
        compressed_transactions = Transaction(compte_id=self.id, created_at=last_day, description=f"Situation au {last_day.strftime('%d/%m/%Y')}", amount=transactions.get_total_amount())
        compressed_transactions.save()
        # On supprime les transactions
        transactions.exclude(id=compressed_transactions.id).delete()

    def pay_salary_if_due(self):
        """
        Verse le salaire si une semaine s'est écoulée depuis le dernier paiement.
        """
        from django.utils import timezone
        now = timezone.now()
        if not self.last_salary_payment or (now - self.last_salary_payment).days >= 7:
            self.add_money(self.salary, description=_('Weekly salary payment'))
            self.last_salary_payment = now
            self.save()

    def __str__(self):
        return self.name

class TransactionQuerySet(models.query.QuerySet):
    def get_total_amount(self):
        return self.aggregate(models.Sum('amount'))['amount__sum'] or 0

class TransactionManager(models.Manager):
    def get_queryset(self):
        return TransactionQuerySet(self.model, using=self._db)
    def get_total_amount(self):
        return self.aggregate(models.Sum('amount'))['amount__sum'] or 0


class Transaction(models.Model):
    # protected $fillable = ['compte_id', 'amount', 'type', 'description'];
    compte = models.ForeignKey(Compte, on_delete=models.CASCADE, related_name='transactions', verbose_name=_('Account'))
    amount = models.FloatField(verbose_name=_('Amount'))
    description = models.TextField(null=True, blank=True, verbose_name=_('Description'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created at'))

    objects = TransactionManager()

    def __str__(self):
        return f"{self.compte.name} - {self.amount}"



# Create your models here.