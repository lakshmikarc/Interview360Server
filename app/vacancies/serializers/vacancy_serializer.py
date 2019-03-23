from . import serializers, Vacancy
from common.serializers.base_vacancy_serializer import BaseVacancySerializer
from django.db import transaction
from skills.models import Skill
from skills.serializers import SkillSerializer
from companies.models import Company
from common.serializers.base_company_serializer import BaseCompanySerializer
from common.serializers.base_interview_serializer import (
    BaseInterviewSerializer
)
from vacancies.index import VacancyIndex

from vacancies.fields import SkillsField


class VacancySerializer(BaseVacancySerializer):
    """Serializer for vacancies object."""

    title = serializers.CharField(max_length=255, required=True)
    description = serializers.CharField(required=False)
    salary = serializers.DecimalField(
        max_digits=6, decimal_places=2, required=True)
    company_id = serializers.IntegerField(required=True, write_only=True)
    company = serializers.SerializerMethodField(read_only=True)
    interviews = serializers.SerializerMethodField(read_only=True)
    skills = SkillsField()

    class Meta:
        """Metaclass serializer."""

        model = BaseVacancySerializer.Meta.model
        fields = BaseVacancySerializer.Meta.fields + [
            'company',
            'skills',
            'interviews'
        ]

    def get_skills(self, obj):
        """Return skills list."""

        skills = obj.skills.all()
        return SkillSerializer(skills, many=True, read_only=True).data

    def get_company(self, vacancy):
        """Return serialized company."""

        company = Company.objects.get(id=vacancy.company_id)
        return BaseCompanySerializer(company, read_only=True).data

    def get_interviews(self, vacancy):
        """Receive list of vacancies interviews."""

        interviews = vacancy.interviews.all()
        return BaseInterviewSerializer(interviews, many=True).data

    def create(self, data):
        """Create new instance of Vacancy and add Skills objects to it."""

        try:
            with transaction.atomic():
                skills = data.pop('skills', None)
                vacancy = Vacancy.objects.create(**data)
                vacancy.skills.set(skills)
                VacancyIndex.store_index(vacancy)
                return vacancy
        except BaseException:
            return False

    def update(self, instance, data):
        """Update vacancy parameters."""

        with transaction.atomic():
            instance.title = data.get('title', instance.title)
            instance.description = data.get(
                'description', instance.description)
            instance.salary = data.get('salary', instance.salary)
            instance.skills.set(data.get('skills', []))
            instance.save()
            VacancyIndex.store_index(instance)
            return instance
