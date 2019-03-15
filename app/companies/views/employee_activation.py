from . import (
    Response,
    get_object_or_404,
    User,
    Company,
    EmployeeForm,
    status,
    IsAuthenticated,
    TokenAuthentication,
    EmployeePermission)
from rest_framework.views import APIView


class EmployeeActivationView(APIView):
    """View class responsible for activation of the new user."""

    def put(self, request, company_pk=None):
        """Update the employees of company."""

        form = EmployeeForm(request.data)

        if form.submit():
            return Response(
                {'message': 'You was sucessfully added to the company!'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'errors': form.errors},
                status=status.HTTP_400_BAD_REQUEST
            )
