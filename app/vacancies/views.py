from django.shortcuts import render
from rest_framework import viewsets
from .models import Vacancy
from .serializers import VacancySerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication

class VacancyViewSet(viewsets.ModelViewSet):
    """ View class for Vacancy """
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, )
    queryset = Vacancy.objects.all()
    serializer_class = VacancySerializer
