from . import (
    TransactionTestCase, datetime, Company,
    InterviewSerializer, mock, CompanyMember, Vacancy, InterviewEmployee,
    Interview, HR, CANDIDATE, User
)

import ipdb


class InterviewSerializerTests(TransactionTestCase):
    """Tests for InterviewSerializer serializer."""

    fixtures = [
        "skill.yaml",
        "user.yaml",
        "company.yaml",
        "vacancy.yaml",
        "interview.yaml"
    ]

    def setUp(self):
        """Set up test dependencies."""

        self.company = Company.objects.first()
        date = datetime.datetime.now() + datetime.timedelta(days=10)
        self.hr = self.company.get_employees_with_role(HR)[-1]
        self.vacancy = self.company.vacancy_set.first()
        self.candidate = self.company.get_employees_with_role(CANDIDATE)[-1]
        self.interview = self.vacancy.interviews.first()
        date = datetime.datetime.now() + datetime.timedelta(days=10)
        self.form_data = {
            'candidate_email': self.candidate.email,
            'vacancy_id': self.vacancy.id,
            'interviewee_ids': [
                self.hr.email
            ],
            'assigned_at': date
        }

    def test_succes_validation(self):
        """Test that serializer's validation is passed."""

        serializer = InterviewSerializer(data=self.form_data)
        self.assertTrue(serializer.is_valid())

    def test_failed_validation(self):
        """Test that serializer's validation is failed."""

        serializer = InterviewSerializer(data={})
        self.assertFalse(serializer.is_valid())

    def test_failed_validation_vacancy_is_abscent(self):
        """Test serializer's validation failed if vacancy does not exists."""

        self.form_data['vacancy_id'] = 100
        serializer = InterviewSerializer(data=self.form_data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue('vacancy_id' in serializer.errors)

    def test_failed_validation_vacancy_is_unactive(self):
        """Test serializer's validation failed is vacancy is not active."""

        vacancy = Vacancy.objects.create(
            title="Vacancy name", description="Description",
            company_id=self.company.id, salary=120.00, active=False
        )
        self.form_data['vacancy_id'] = vacancy.id
        serializer = InterviewSerializer(data=self.form_data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue('vacancy_id' in serializer.errors)

    @mock.patch('authorization.models.User.objects.get_or_create')
    def test_create_new_candidate_if_there_are_no_such_candidate(
            self, user_mock):
        """Test creating the new candidate if it is not abscent."""

        user_mock.objects = mock.MagicMock()
        user_mock.objects = mock.MagicMock()
        user_mock.get_or_create = mock.MagicMock()
        user_mock.return_value = User(id=1)

        self.form_data['candidate_email'] = 'ololosh@gmail.com'
        serializer = InterviewSerializer(data=self.form_data)
        serializer.is_valid()
        serializer.save()
        assert user_mock.called, True
        # self.assertTrue(serializer.is_valid())

    def test_failed_validation_if_assigned_at_less_than_current_date(self):
        """
        Test serializer's validation failed.

        Assigned_at isless than current time.
        """

        date = datetime.datetime.now() + datetime.timedelta(days=-10)
        self.form_data['assigned_at'] = date

        serializer = InterviewSerializer(data=self.form_data)
        self.assertFalse(serializer.is_valid())
        self.assertTrue('assigned_at' in serializer.errors)

    @mock.patch('interviews.models.Interview.objects.create')
    @mock.patch('interviews.models.InterviewEmployee.objects.create')
    def test_success_interview_creation(
            self,
            inteview_employee_class_mock,
            inteview_class_mock):
        """Test success creation of the interview."""

        inteview_employee_class_mock.objects = mock.MagicMock()
        inteview_employee_class_mock.objects.create = mock.MagicMock()
        inteview_employee_class_mock.objects.create.return_value = (
            InterviewEmployee(id=1)
        )

        inteview_class_mock.objects = mock.MagicMock()
        inteview_class_mock.objects.create = mock.MagicMock()
        inteview_class_mock.objects.create.return_value = Interview(id=1)

        serializer = InterviewSerializer(data=self.form_data)
        serializer.is_valid()

        serializer.save()
        self.assertTrue(inteview_class_mock.called)

    @mock.patch('interviews.models.InterviewEmployee.objects.create')
    def test_success_interview_employee_creation(
            self, inteview_employee_class_mock):
        """Test success creation of InterviewEmployee instance."""

        inteview_employee_class_mock.objects = mock.MagicMock()
        inteview_employee_class_mock.objects.create = mock.MagicMock()
        inteview_employee_class_mock.objects.create.return_value = (
            InterviewEmployee(id=1)
        )

        serializer = InterviewSerializer(data=self.form_data)
        serializer.is_valid()

        serializer.save()
        self.assertTrue(inteview_employee_class_mock.called)
        self.assertTrue(inteview_employee_class_mock.call_count, 1)

    def test_failed_interview_employee_creation(self):
        """Test failed creation of Interviewemployee for the abscent user."""

        self.form_data['interviewee_ids'] = 100

        serializer = InterviewSerializer(data=self.form_data)

        self.assertFalse(serializer.is_valid())
        self.assertTrue('interviewee_ids' in serializer.errors)

    def test_success_update_of_the_interview(self):
        """Test success updating of the interview instance."""

        date = datetime.datetime.now() + datetime.timedelta(days=31)
        date = date.replace(second=0, microsecond=0, tzinfo=None)
        self.form_data['assigned_at'] = str(date)

        serializer = InterviewSerializer(
            self.interview, data=self.form_data, partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        self.interview.refresh_from_db()
        self.assertEqual(self.interview.assigned_at.replace(
            second=0, microsecond=0, tzinfo=None), date
        )
