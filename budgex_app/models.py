
from django.db import models
import re
from datetime import date
from django.utils.translation import gettext as _

# Create your models here.

class userManager(models.Manager):
    def get_help_text(self):
        return _(
            "Your password must contain at least 8 characters, including at least one uppercase letter, "
            "one lowercase letter, one digit, and one special character (!@#$%^&* etc.)."
        )
    def validator(self,postData):

        errors={}
        password = postData.get('password', '')
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]+$')
        if not EMAIL_REGEX.match(postData['email']):
            errors['email_error']="Invalid Email"
        users = User.objects.filter(email = postData['email'])
        if users:
            errors['email_format']="The email is alredy exist !"
        if len(postData['first_name'])<2:
            errors["first_name"]="The length of first name should be more than 2 characters"
        if len(postData['last_name'])<2:
            errors["last_name"]="The length of last name should be more than 2 characters"
        if len(postData['email'])<2:
            errors['email']="The length of email should be more than 2 characters"
        if len(password) < 8:
            errors["length"] = _("Password must be at least 8 characters long.")

        if not any(char.isdigit() for char in password):
            errors["digit"] = _("Password must contain at least one digit.")

        if not any(char.islower() for char in password):
            errors["lowercase"] = _("Password must contain at least one lowercase letter.")

        if not any(char.isupper() for char in password):
            errors["uppercase"] = _("Password must contain at least one uppercase letter.")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            errors["special_char"] = _("Password must contain at least one special character.")

        if postData['password']!=postData['confirm_pw']:
            errors['confirm_pw']="The passwords is not matched"
        return errors
    
class User(models.Model):
    first_name=models.CharField(max_length=45)
    last_name=models.CharField(max_length=45)
    email=models.CharField(max_length=255,unique=True)
    birthdate = models.DateField(null=True, blank=True)
    password=models.CharField(max_length=128)
    created_at=models.DateField(auto_now=True)
    updated_at=models.DateField(auto_now=True)
    objects=userManager()



class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)



class Budget(models.Model):
    CURRENCY_CHOICES = [
        ('USD', 'United States Dollar'),
        ('EUR', 'Euro'),
        ('GBP', 'British Pound'),
        # Add more currencies as needed
    ]

    RECURRENCE_CHOICES = [
        ('once', 'Once'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('biweekly', 'Biweekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budgets")
    name = models.CharField(max_length=255, blank=False, null=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='USD')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="budgets")
    recurrence = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, default='monthly')
    start_date = models.DateField()

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="transactions")
    budget = models.ForeignKey('Budget', on_delete=models.CASCADE, related_name="transactions")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=7, choices=TRANSACTION_TYPES)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions")
    description = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)




