from . import (User, TestCase, RestorePasswordForm,
               override_settings, Token, mock)
import django.core.mail as mail


class RestorePasswordFormTests(TestCase):
    """Test RestorePasswordForm class."""

    def setUp(self):
        """Set up test credentials."""

        self.user = User.objects.create(email="example@mail.com")
        self.user.set_password('12345678')
        self.user.save()

    def test_success_form_validation(self):
        """Test form validation if all necessary parameters are passed."""

        form_data = {'email': 'example@mail.com'}
        form = RestorePasswordForm(form_data)
        self.assertEqual(form.is_valid(), True)

    def test_failed_form_validation(self):
        """Test form validation if parameters are missing."""

        form = RestorePasswordForm({})
        self.assertEqual(form.is_valid(), False)

    def test_success_submit(self):
        """Test success call of submit."""

        form_data = {'email': self.user.email}
        form = RestorePasswordForm(form_data)
        self.assertEqual(form.submit(), True)

    def test_failed_submit(self):
        """Test failed call of submit."""

        form_data = {}
        form = RestorePasswordForm(form_data)
        self.assertEqual(form.submit(), False)

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_mail_was_sended(self):
        """Test success mail sending after password restore."""

        form_data = {'email': 'example@mail.com'}
        form = RestorePasswordForm(form_data)
        form.submit()
        self.assertEqual(len(mail.outbox), 1)

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
    def test_mail_was_not_sended(self):
        """Test mail sending after failed password restore."""

        form_data = {}
        form = RestorePasswordForm(form_data)
        form.submit()
        self.assertEqual(len(mail.outbox), 0)

    @mock.patch('rest_framework.authtoken.models.Token.objects.get_or_create')
    def test_token_success_creation(self, token_mock):
        """Test token creation after success restore password."""

        token_mock.user = self.user
        token_mock.return_value = ("12345", 12)
        form_data = {'email': 'example@mail.com'}
        form = RestorePasswordForm(form_data)
        form.submit()

        self.assertTrue(token_mock.called)

    @mock.patch('rest_framework.authtoken.models.Token.objects.get_or_create')
    def test_token_failed_creation(self, token_mock):
        """Test token creation after failed restore password."""

        token_mock.user = self.user
        token_mock.return_value = ("12345", 12)
        form_data = {}
        form = RestorePasswordForm(form_data)
        form.submit()

        self.assertFalse(token_mock.called)
