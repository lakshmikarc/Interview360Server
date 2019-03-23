from . import (
    viewsets, list_route, Response, status, get_object_or_404,
    IsAuthenticated, TokenAuthentication, WorkplacePermissions
)
from rest_framework.views import APIView
from resumes.models import Resume, Workplace


class WorkplacesDeleteApiView(APIView):
    """Class for deleting the existing workplace from the resume."""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, WorkplacePermissions, )

    def delete(self, request, id=None, resume_id=None):
        """Delete existing workplace."""

        workplace = get_object_or_404(Workplace, resume_id)
        workplace.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
