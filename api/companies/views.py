from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination

from companies.models import Company
from companies.serializer import CompanySerializer


class CompanyViewSet(viewsets.ModelViewSet):
    serializer_class = CompanySerializer
    queryset = Company.objects.all().order_by('last_update')
    pagination_class = PageNumberPagination
