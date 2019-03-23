from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager
)
from django.apps import apps
from roles.models import get_role
from django.contrib.contenttypes.fields import GenericRelation

from .user import User
