from . import APITestCase, datetime, Token, Company, HR, CANDIDATE
import ipdb


class InterviewViewSetTests(APITestCase):
    """Tests for InterviewViewSet class."""

    fixtures = [
        "skill.yaml",
        "user.yaml",
        "auth_token.yaml",
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
        self.token = Token.objects.get(user=self.hr)
        self.candidate_token = Token.objects.get(user=self.candidate)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        self.form_data = {
            'candidate_email': self.candidate.email,
            'vacancy_id': self.vacancy.id,
            'interviewee_ids': [
                self.hr.email
            ],
            'assigned_at': date
        }
        self.url = "/api/v1/companies/{}/interviews/".format(self.company.id)

    def test_success_list_receiving(self):
        """Test success receiving list of the interviews."""

        response = self.client.get(self.url, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)

    # TODO Fix after rebuilding interview tests with factory
    # def test_success_retrieve_action(self):
    #     """Test success receiving detail interview."""
    #
    #     self.client.credentials(
    #       HTTP_AUTHORIZATION='Token ' + self.candidate_token.key
    #     )
    #     response = self.client.get(
    #         self.url + "{}/".format(self.interview.id), format='json'
    #     )
    #     self.assertEqual(response.status_code, 200)

    def test_success_interview_creation(self):
        """Test success creation of the interview."""

        response = self.client.post(self.url, self.form_data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertTrue('interview' in response.data)

    def test_failed_interview_creation(self):
        """Test failed creation of the interview."""

        response = self.client.post(self.url, {}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_success_interview_update(self):
        """Test success Interview's instance update."""

        response = self.client.put(
            self.url + "{}/".format(self.interview.id), self.form_data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue('interview' in response.data)

    def test_success_interview_delete(self):
        """Test success Interview's instance delete."""

        response = self.client.delete(
            self.url + "{}/".format(self.interview.id), format='json'
        )
        self.assertEqual(response.status_code, 204)
