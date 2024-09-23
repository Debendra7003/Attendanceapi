from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser # type: ignore
# from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
import re

from pytz import timezone
# Create your models here.


class UserManager(BaseUserManager):
    def create_user(self, email, name, password=None,password2=None):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email,name, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user
# ------------------------------------Admin Register model-------------------------------------
class User(AbstractBaseUser):
    email = models.EmailField(verbose_name="Email",max_length=255,unique=True) 
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

# -------------------------Custom validator for alphanumeric Employee_code--------------------------
def validate_employee_code(value):
    if not re.match(r'^[A-Za-z0-9]+$', value):
        raise ValidationError("Employee code must be alphanumeric.")


# ------------------------------------Employee Register model-------------------------------------
class Employee(models.Model):
    date = models.DateField()  # Users can enter past or present dates
    zone = models.CharField(max_length=100)
    employee_code = models.CharField(
        max_length=10,
        unique=True,
        validators=[validate_employee_code])
            # RegexValidator(regex=r'^[a-zA-Z0-9]*$', message='Employee code must be alphanumeric')])
    employee_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    supervisor_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.employee_name} ({self.employee_code})"
    
    
# ------------------------------------Otp store for forget password  model-------------------------------------
class OTP(models.Model):
    email = models.EmailField(max_length=100)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    # def is_valid(self):
    #      return (datetime.now(timezone.utc) - self.created_at).total_seconds() < 600
        # OTP is valid for 10 minutes
        # return (datetime.now() - self.created_at).total_seconds() < 600
        #  return (timezone.now() - self.created_at).total_seconds() < 600



# ------------------------------------Employee Attendance model-------------------------------------
class EmployeeAttendance(models.Model):
    # Fields for the Employee Attendance model
    date_of_work = models.DateField(unique=True)
    zone = models.CharField(max_length=100)
    employee_code = models.CharField(max_length=10,validators=[validate_employee_code])
    employee_name = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    supervisor_name = models.CharField(max_length=100,default="NA")   
    # SK, SSK, USK with OT fields that can only be 0 or 1
    sk = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    sk_ot = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    ssk = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    ssk_ot = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    usk = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1)])
    usk_ot = models.IntegerField(validators=[MinValueValidator(0), MaxValueValidator(1)])

    # Attendance field
    attendance = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.employee_name} - {self.employee_code}'