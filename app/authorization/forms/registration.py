from . import forms, transaction, User, Token
from django.db.utils import IntegrityError
from django.db import connection
from common.advisory_lock import advisory_lock
from profiles.index import UserIndex
import elasticsearch


class RegistrationForm(forms.Form):
    """Registration form class."""

    email = forms.CharField(max_length=255, strip=True)
    password = forms.CharField(max_length=255, min_length=6)
    password_confirmation = forms.CharField(max_length=255, min_length=6)

    def clean(self):
        """Clean data and add custom validation."""

        cleaned_data = super(RegistrationForm, self).clean()

        password = cleaned_data.get('password')
        password_confirmation = cleaned_data.get('password_confirmation')

        if password and password_confirmation:
            if password != password_confirmation:
                self.add_error(
                    'password_confirmation',
                    'Does not match password')
                raise forms.ValidationError("Does not match password")
        return cleaned_data

    def submit(self):
        """Create new user."""

        if not self.is_valid():
            return False

        try:
            with advisory_lock('User'):
                with transaction.atomic():
                    user = User(email=self['email'].value())
                    user.set_password(self['password'].value())
                    user.save()
                    self.token = Token.objects.create(user=user)
                    UserIndex.store_index(user)
                    return True
        except IntegrityError:
            self.add_error('email', 'Already present')
            return False
        except elasticsearch.exceptions.ConnectionError:
            self.add_error('email', 'There is an indexing error occured')
            return False
