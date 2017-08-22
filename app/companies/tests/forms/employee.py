from . import (mock, TransactionTestCase, Token, EmployeeForm,
               Company, CompanyMember, User, Role, datetime)
import ipdb

class EmployeeFormTest(TransactionTestCase):
    """ Tests for the EmployeeFormTest class """

    def setUp(self):
        """ Set up test dependencies """

        self.user = User.objects.create(email="example@mail.com")
        self.company = Company.objects.create(name="Test",
                                         city="Test",
                                         start_date=datetime.date.today())
        self.token = Token.objects.create(user=self.user)
        self.role = Role.objects.create(name='owner')
        self.company_member = CompanyMember.objects.create(
            user=self.user, company=self.company, role=self.role
        )
        self.form_data = {
            'company_id': self.company.id,
            'token': self.token.key,
            'password': 'aaaaaa',
            'password_confirmation': 'aaaaaa'
        }

    def test_success_form_validation(self):
        """ Test success form validation with all necessary parameters """

        form = EmployeeForm(self.form_data)
        self.assertTrue(form.is_valid())

    def test_failed_form_validation(self):
        """ Test failed form validation """

        form = EmployeeForm({})
        self.assertFalse(form.is_valid())

    def test_failed_password_matching(self):
        """ Test failed form validation due to different password """

        form_data = {
            'company_id': self.company.id,
            'token': self.token.key,
            'password': 'aaaaaa',
            'password_confirmation': 'bbbbbb'
        }

        form = EmployeeForm(form_data)
        self.assertFalse(form.is_valid())

    @mock.patch.object(User, 'save')
    @mock.patch('django.contrib.auth.models.User')
    def test_saving_user_information(self, user_class_mock, user_save_mock):
        """ Test calling save() method on User """

        user_class_mock.objects = mock.MagicMock()
        user_class_mock.objects.create = mock.MagicMock()
        user_class_mock.objects.create.return_value = User(id=1)

        form = EmployeeForm(self.form_data)
        form.submit()
        self.assertTrue(user_save_mock.called)

    def test_updating_user_password(self):
        """ Test updating user password """

        form = EmployeeForm(self.form_data)
        form.submit()
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.form_data['password']))

    def test_company_member_updated(self):
        """ Test update of CompanyMember instance 'active' field """

        form = EmployeeForm(self.form_data)
        form.submit()

        self.company_member.refresh_from_db()
        self.assertTrue(self.company_member.active)

    def test_user_does_not_have_company_member(self):
        """ Test validation failure if user does not have a company_member instance """

        user = User.objects.create(email="batman@superman.com")
        token = Token.objects.create(user=user)
        form_data = {
            'company_id': self.company.id,
            'token': token.key,
            'password': 'aaaaaa',
            'password_confirmation': 'aaaaaa'
        }

        form = EmployeeForm(form_data)
        self.assertFalse(form.submit())
