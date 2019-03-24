from django.db import models
from authorization.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.contenttypes.fields import GenericRelation
from .managers import CompanyManager


class Company(models.Model):
    """Base company model."""

    ORDER_FIELDS = (
        ('employees__count', 'Employees count'),
        ('vacancy__count', 'Vacancies count'),
        ('vacancy__interviews__count', 'Interviews count'),
        ('created_at', 'Created at')
    )

    name = models.CharField(max_length=255, null=False)
    start_date = models.DateField(null=True)
    description = models.TextField()
    city = models.CharField(null=True, max_length=255)
    country = models.CharField(null=True, max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    employees = models.ManyToManyField(
        'authorization.User', through='CompanyMember')
    images = GenericRelation('attachments.Image')
    specialties = models.ManyToManyField('companies.Specialty')
    objects = CompanyManager()

    class Meta:
        """Metaclass for company model."""

        db_table = 'companies'

    def get_employees_with_role(self, role):
        """
        Return list of employees who are belonging to the companyself.

        With particular role.
        """

        objects = CompanyMember.objects.filter(
            company_id=self.id, role=role
        ).prefetch_related('user')
        return list(map(lambda member: member.user, objects))


class CompanyMember(models.Model):
    """CompanyMember model, which is used for `through` association."""

    COMPANY_OWNER = 1
    HR = 2
    CANDIDATE = 3
    EMPLOYEE = 4

    ROLES = (
        (COMPANY_OWNER, 'Company Owner'),
        (HR, 'HR'),
        (CANDIDATE, 'Candidate'),
        (EMPLOYEE, 'Employee')
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    role = models.IntegerField(
        default=EMPLOYEE, choices=ROLES, db_index=True, null=False
    )
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Metaclass for company members model."""

        db_table = 'company_members'
        index_together = unique_together = [
            ['user', 'company']
        ]


class Specialty(models.Model):
    """Specialty of the company model."""

    class Meta:
        """Specialty model metaclass."""

        db_table = 'specialties'

    name = name = models.CharField(max_length=255, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
