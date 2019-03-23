from . import (
    render, viewsets, status, Response, get_object_or_404,
    IsAuthenticated, TokenAuthentication, Count,
    CompanySerializer, CompaniesSerializer, Company, CompanyPermissions,
    CompanyIndex, list_route, CompanySearch, CompanyForm, CompaniesFilter,
    CompaniesQuery, QueryParser, CitiesService, Specialty
)


def get_company(user, pk):
    """Receives particular company from the queryset."""

    queryset = user.companies.all()
    company = get_object_or_404(queryset, pk=pk)
    return company


class CompaniesViewSet(viewsets.ModelViewSet):
    """Viewset for company actions."""

    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated, CompanyPermissions, )
    queryset_parser = QueryParser({
        'role': int,
        'order': str
    })

    def get_serializer_class(self):
        """Return specific serializer for action."""

        if self.action == 'list':
            return CompaniesSerializer
        else:
            return CompanySerializer

    def get_queryset(self):
        """Return scope of companies which current user belongs to."""

        if self.action == 'list':
            params = self.queryset_parser.parse(self.request.query_params)
            query = CompaniesQuery(params, self.request.user)
            return query.list()
        else:
            return self.request.user.companies.prefetched_detail()

    def create(self, request):
        """Create a new company."""

        form = CompanyForm(
            obj=Company(), params=request.data, current_user=request.user
        )
        if form.submit():
            serializer = CompanySerializer(form.obj)
            return Response({'company': serializer.data},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({'errors': form.errors},
                            status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        """Update an existent company."""

        company = self.get_object()
        form = CompanyForm(
            obj=company, params=request.data, current_user=request.user
        )
        if form.submit():
            serializer = CompanySerializer(form.obj)
            return Response({'company': serializer.data},
                            status=status.HTTP_200_OK)
        else:
            return Response({'errors': form.errors},
                            status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """Delete selected company."""

        company = self.get_object()
        CompanyIndex.get(id=company.id).delete()
        company.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @list_route(methods=['get'])
    def search(self, request):
        """Search companies."""

        query = request.query_params.get('q')
        search = CompanySearch()
        results = search.find(query)
        return Response({'companies': results})

    @list_route(methods=['get'])
    def filters(self, request):
        """Get filters for the companies."""

        filters = CompaniesFilter({})
        return Response({'filters': filters.data})

    @list_route(methods=['get'])
    def cities(self, request):
        """Find city with country by name."""

        cities_service = CitiesService()
        response = cities_service.find_by_name(
            request.query_params.get('name'))
        return Response({'cities': response})
