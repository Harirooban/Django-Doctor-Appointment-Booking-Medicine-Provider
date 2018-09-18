from django.db import models
from django import forms


class users(models.Model):
    userId = models.IntegerField(primary_key=True)
    password = models.CharField(max_length=300)
    email = models.CharField(max_length=300)
    firstname = models.CharField(max_length=300)
    lastname = models.CharField(max_length=300)


class categories(models.Model):
    object = None
    categoryId = models.IntegerField(primary_key=True,)
    name = models.CharField(max_length=300)
    image = models.FileField(upload_to='images/', null=True, verbose_name="")

    def __str__(self):
        return '{}'.format(self.name)

class products(models.Model):
    objects = None
    productId = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=300)
    price = models.DecimalField('Price', max_digits=20, decimal_places=10, blank=True, null=True)
    description = models.CharField(max_length=300)
    image = models.FileField(upload_to='images/', blank=True, null=True, verbose_name="")
    categoryId = models.ForeignKey("categories")




class kart(models.Model):
    userId = models.ForeignKey("users")
    productId = models.ForeignKey("products")


class Patient(models.Model):
    objects = None
    name = models.CharField(max_length=300)
    phone = models.IntegerField()
    Email = models.EmailField(max_length=100)
    gender = models.CharField(max_length=300)
    DoctorName = models.CharField(max_length=300)
    Spec = models.CharField(max_length=300)
    EmailId = models.CharField(max_length=100)
    Date = models.CharField(max_length=100)
    Time = models.CharField(max_length=100)
    visit = models.CharField(max_length=200)

    def __str__(self):
        return 'Patient: {}'.format(self.Email, self.gender)



class admin(models.Model):
    userId = models.IntegerField(primary_key=True)
    password = models.CharField(max_length=300)
    email = models.EmailField(max_length=300)
    firstname = models.CharField(max_length=300)
    lastname = models.CharField(max_length=300)


class Doctor(models.Model):
    DoctorId = models.IntegerField(primary_key=True)
    DoctorName = models.CharField(max_length=100)
    PhoneNumber = models.IntegerField()
    SpecilistIn = models.CharField(max_length=100)
    EmailId = models.EmailField(max_length=100)
    password = models.CharField(max_length=100)


class order(models.Model):
    name = models.CharField(max_length=300)
    price = models.DecimalField('medium', max_digits=20, decimal_places=10, blank=True, null=True)
    description = models.CharField(max_length=300)
    image = models.FileField(upload_to='products', null=True, verbose_name="")
    productId = models.IntegerField(null=True)
    userId = models.ForeignKey("users", on_delete=models.CASCADE)


class Confirm(models.Model):
    name = models.CharField(max_length=300)
    phone = models.IntegerField()
    Email = models.EmailField(max_length=100)
    gender = models.CharField(max_length=300)
    Date = models.CharField(max_length=100)
    Time = models.CharField(max_length=100)
    visit = models.CharField(max_length=200)
    EmailId = models.EmailField(max_length=100)



