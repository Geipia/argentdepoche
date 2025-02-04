from django.db import models
from django.contrib.auth.models import User

class Compte(models.Model):
    # protected $fillable = ['user_id', 'manager_id', 'name', 'salary', 'total'];
    name = models.CharField(max_length=24)
    salary = models.FloatField(default=0)
    total = models.FloatField(default=0)
    manager = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comptes')
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mon_compte')

    def __str__(self):
        return self.name

# Create your models here.