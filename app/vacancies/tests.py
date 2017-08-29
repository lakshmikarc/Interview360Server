from django.test import TransactionTestCase
from rest_framework.test import APITestCase
from .models import Vacancy
from authorization.models import User
from companies.models import Company
from rest_framework.authtoken.models import Token
from skills.models import Skill
import datetime
from decimal import *
from .serializers import VacancySerializer
import mock

class VacancyViewSetTests(APITestCase):
    """ Tests for VacancyViewSet class """

    def setUp(self):
        """ Setting up test dependencies """

        self.user = User.objects.create(email="example1@mail.com")
        self.company = Company.objects.create(name="Test",
                                         city="Test",
                                         start_date=datetime.datetime.now())
        self.token = Token.objects.create(user=self.user)
        self.skill = Skill.objects.create(name="Computer Science")
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.vacancy = Vacancy.objects.create(
            title="Vacancy name", description="Description",
            company_id=self.company.id, salary=120.00)
        self.url = "/api/v1/companies/{}/vacancies/".format(self.company.id)
        self.form_data = {
            'title': 'Test',
            'description': 'Test',
            'salary': '150.00',
            'company_id': self.company.id,
            'skills': [
                self.skill.id
            ]
        }

    def test_success_list_receiving(self):
        """ Test success receiving of the vacancies list """

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_success_vacancy_creation(self):
        """ Test success vacancy creation """

        response = self.client.post(self.url, self.form_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual('vacancy' in response.data, True)

    def test_failed_vacancy_creation(self):
        """ Test failed creation of the vacancy """

        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, 400)

    def test_success_vacancy_update(self):
        """ Test success update of the vacancy """

        response = self.client.put(
            self.url + "{}/".format(self.vacancy.id),
            self.form_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('vacancy' in response.data)

    def test_success_delete_vacancy(self):
        """ Test success vacancy deletion """

        response = self.client.delete(self.url + "{}/".format(self.vacancy.id))
        self.assertEqual(response.status_code, 204)

class VacancySerializerTest(TransactionTestCase):
    """ Test class for VacanciesSerializer """

    def setUp(self):
        """ Setting up testing dependencies """

        self.user = User.objects.create(email="example1@mail.com")
        self.company = Company.objects.create(name="Test",
                                         city="Test",
                                         start_date=datetime.datetime.now())
        self.token = Token.objects.create(user=self.user)
        self.skill = Skill.objects.create(name="Computer Science")
        self.vacancy = Vacancy.objects.create(
            title="Vacancy name", description="Description",
            company_id=self.company.id, salary=120.00)
        self.url = "/api/v1/companies/{}/vacancies/".format(self.company.id)
        self.form_data = {
            'title': 'Test',
            'description': 'Test',
            'salary': '150.00',
            'company_id': self.company.id,
            'skills': [
                self.skill.id
            ]
        }

    def test_success_validation(self):
        """ Test that validation successfuly passing """

        serializer = VacancySerializer(data=self.form_data)
        self.assertTrue(serializer.is_valid())

    def test_failed_validation(self):
        """ Test that validation fails """

        serializer = VacancySerializer(data={})
        self.assertFalse(serializer.is_valid())

    def test_failed_skills_are_empty(self):
        """ Test validation failure if skills is empty """

        form_data = {
            'title': 'Test',
            'description': 'Test',
            'salary': '150.00',
            'company_id': self.company.id
        }

        serializer = VacancySerializer(data=form_data)
        self.assertFalse(serializer.is_valid())

    @mock.patch('vacancies.models.Vacancy.objects.create')
    def test_vacancy_created(self, vacancy_mock):
        """ Test success calling 'create' for Vacancy """

        vacancy_mock.objects = mock.MagicMock()
        vacancy_mock.objects.create = mock.MagicMock()

        serializer = VacancySerializer(data=self.form_data)
        self.assertTrue(serializer.is_valid())

        serializer.save()

        self.assertTrue(vacancy_mock.called)

    def test_skills_was_setted(self):
        """ Test success adding of skills to vacancy """

        serializer = VacancySerializer(data=self.form_data)
        self.assertTrue(serializer.is_valid())

        serializer.save()

        vacancy = Vacancy.objects.last()
        self.assertEqual(len(vacancy.skills.all()), 1)

    def test_vacancy_was_updated(self):
        """ Test success updating of the vacancy """

        form_data = {
            'title': 'Test11',
            'description': 'Test',
            'salary': '150.00',
            'company_id': self.company.id,
            'skills': [
                self.skill.id
            ]
        }

        serializer = VacancySerializer(self.vacancy, data=form_data,
                                       partial=True)
        serializer.is_valid()

        v = serializer.save()
        self.assertTrue(v.title == form_data['title'])

    def test_number_of_skills_was_changed(self):
        """ Test that new skills were applly """

        new_skill = Skill.objects.create(name="Python")
        form_data = {
            'title': 'Test11',
            'description': 'Test',
            'salary': '150.00',
            'company_id': self.company.id,
            'skills': [
                self.skill.id,
                new_skill.id
            ]
        }

        serializer = VacancySerializer(self.vacancy, data=form_data,
                                       partial=True)

        serializer.is_valid()

        v = serializer.save()
        self.assertEqual(len(v.skills.all()), 2)
