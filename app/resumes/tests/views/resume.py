from . import (
    APITestCase, mock, HR, EMPLOYEE, CANDIDATE,
    Skill, Company, Resume, Token, User
)
from resumes.index import ResumesIndex
import ipdb


class ResumeViewTest(APITestCase):
    """Tests for ResumeViewTest."""

    fixtures = [
        'user.yaml',
        'company.yaml',
        'skill.yaml',
        'resume.yaml'
    ]

    def setUp(self):
        """Set up testing dependencies."""

        self.resume = Resume.objects.first()
        self.company = Company.objects.first()
        self.user = User.objects.first()
        self.token = Token.objects.create(user=self.user)
        self.skills = [s.id for s in Skill.objects.filter(id__in=[1, 2])]
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.params = {
            'title': 'Python developer',
            'user_id': self.user.id,
            'skills': self.skills,
            'description': 'Resume',
            'salary': 120000,
            'workplaces': [
                {
                    'position': 'QA',
                    'company': self.company.name,
                    'description': 'Bla-bla',
                    'start_date': '2015-02-01',
                    'end_date': '2017-02-01'
                }
            ],
            'contact': {
                'resume_id': self.resume.id,
                'email': self.user.email,
                'phone': '+79214438239'
            }
        }

    def test_success_list_receiving(self):
        """Test success receiving of the list of resumes."""

        response = self.client.get('/api/v1/resumes/', format='json')
        self.assertEqual(len(response.data), 4)

    def test_success_retrieve_resume(self):
        """Test success resume retrieving."""

        response = self.client.get(
            '/api/v1/resumes/{}/'.format(self.resume.id), format='json'
        )
        for key in ['id', 'title', 'description']:
            assert getattr(self.resume, key), response.data[key]

    @mock.patch('common.services.twilio_service.TwilioService')
    @mock.patch('resumes.index.ResumesIndex.store_index')
    def test_success_creation_of_resume(self, resume_index, twilio_mock):
        """Test success creation of the resume."""

        response = self.client.post(
            '/api/v1/resumes/', self.params, format='json')
        self.assertTrue('resume' in response.data)

    @mock.patch('common.services.twilio_service.TwilioService')
    @mock.patch('resumes.index.ResumesIndex.store_index')
    def test_failed_creation_of_resume(self, resume_index, twilio_mock):
        """Test failed creation of the resume."""

        response = self.client.post('/api/v1/resumes/', None, format='json')
        self.assertTrue('errors' in response.data)

    @mock.patch('common.services.twilio_service.TwilioService')
    @mock.patch('resumes.index.ResumesIndex.store_index')
    def test_success_update_of_resume(self, resume_index, twilio_mock):
        """Test success update of a resume."""

        response = self.client.put(
            '/api/v1/resumes/{}/'.format(self.resume.id), self.params,
            format='json'
        )
        self.assertTrue('resume' in response.data)

    @mock.patch.object(ResumesIndex, 'get')
    @mock.patch.object(ResumesIndex, 'delete')
    @mock.patch('resumes.index.ResumesIndex.store_index')
    def test_success_deletion_of_resume(self, resume_index,
                                        delete_resume, get_resume):
        """Test success delete of the resume."""

        response = self.client.delete(
            '/api/v1/resumes/{}/'.format(self.resume.id), format='json'
        )
        assert response.status_code, 204

    @mock.patch('resumes.search.ResumesSearch.find')
    def test_search_action(self, search_mock):
        """Test success search of resume."""

        resume_index = [
            {'id': 1},
            {'id': 2},
            {'id': 3}
        ]
        search_mock.return_value = resume_index
        url = "/api/v1/resumes/search/"
        response = self.client.get(url, {'q': 'buzzword'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['resumes'], resume_index)

    def test_list_action_with_attributes(self):
        """Test receiving of the resumes list with parameters."""

        url = "/api/v1/resumes/"
        self.client.get(url, {
            'salary': {
                'min': 10000,
                'max': 15000
            }
        }, format='json')

    def test_success_receiving_of_filters(self):
        """Test success response on filters receiving."""

        url = "/api/v1/resumes/filters/"
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, 200)
