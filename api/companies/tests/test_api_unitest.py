import json
from unittest import TestCase

import pytest as pytest
from django.test import Client
from django.urls import reverse

from companies.models import Company
from companies.serializer import CompanySerializer


@pytest.mark.django_db
class TestGetCompanies(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.companies_url = reverse('companies-list')

    def test_zero_companies_should_return_empty_list(self) -> None:
        print(self)
        response = self.client.get(self.companies_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    def test_one_company_should_return_list_with_one_company(self) -> None:
        test_company = Company.objects.create(name='Amazon')
        response = self.client.get(self.companies_url)
        response_data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response_data[0]['name'], test_company.name)
        self.assertEqual(response_data[0]['status'], "Hiring")
        self.assertEqual(response_data[0]['application_link'], "")
        self.assertEqual(response_data[0]['notes'], "")

        test_company.delete()


@pytest.mark.django_db
class TestPostCompanies(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.companies_url = reverse('companies-list')

    def test_create_company_with_missing_fields_should_return_error(self) -> None:
        response = self.client.post(self.companies_url)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'name': ['This field is required.']})

    def test_create_company_already_exists_should_return_error(self) -> None:
        Company.objects.create(name='Apple')
        response = self.client.post(self.companies_url, data={'name': 'Apple'})
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {'name': ['company with this name already exists.']})

    def test_create_company_with_only_name_all_fields_should_be_default(self) -> None:
        response = self.client.post(self.companies_url, data={'name': 'Amazon'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'Amazon')
        self.assertEqual(response.data['status'], 'Hiring')
        self.assertEqual(response.data['application_link'], '')
        self.assertEqual(response.data['notes'], '')

    def test_post_company_with_layoffs_status_should_succeed(self) -> None:
        response = self.client.post(self.companies_url, data={'name': 'Amazon', 'status': 'Layoffs'})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['name'], 'Amazon')
        self.assertEqual(response.data['status'], 'Layoffs')

    def test_post_company_with_wrong_status_should_return_error(self) -> None:
        response = self.client.post(self.companies_url, data={'name': 'Amazon', 'status': 'wrong'})
        response_data = json.loads(response.content)
        status_message = response_data['status'][0]
        self.assertEqual(response.status_code, 400)

        self.assertEqual(response.data, {'status': ['"wrong" is not a valid choice.']})
        # or
        self.assertIn('wrong', status_message)
        self.assertIn('is not a valid choice.', status_message)

    @pytest.mark.xfail(raises=AssertionError)
    def test_should_be_ok_if_it_fails(self):
        self.assertEqual(1, 2)

    @pytest.mark.skip(reason='not implemented')
    def test_should_be_skipped(self):
        self.assertEqual(1, 2)