import json
from unittest import TestCase

import pytest as pytest
from django.test import Client
from django.urls import reverse

from companies.models import Company
from companies.serializer import CompanySerializer

companies_url = reverse('companies-list')
pytestmark = pytest.mark.django_db


# ------------------ Test Get Company ------------------ #

def test_zero_companies_should_return_empty_list(client) -> None:
    response = client.get(companies_url)
    assert response.status_code == 200
    assert response.data == []


def test_one_company_should_return_list_with_one_company(client) -> None:
    test_company = Company.objects.create(name='Amazon')
    response = client.get(companies_url)
    response_data = json.loads(response.content)

    assert response.status_code == 200
    assert len(response.data) == 1
    assert response_data[0]['name'] == test_company.name
    assert response_data[0]['status'] == "Hiring"
    assert response_data[0]['application_link'] == ""
    assert response_data[0]['notes'] == ""

    test_company.delete()


# ------------------ Test Post Company ------------------ #

def test_create_company_with_missing_fields_should_return_error(client) -> None:
    response = client.post(companies_url, data={})
    assert response.status_code, 400
    assert response.data, {'name': ['This field is required.']}


def test_create_company_already_exists_should_return_error(client) -> None:
    Company.objects.create(name='Apple')
    response = client.post(companies_url, data={'name': 'Apple'})
    assert response.status_code == 400
    assert response.data == {'name': ['company with this name already exists.']}


def test_create_company_with_only_name_all_fields_should_be_default(client) -> None:
    response = client.post(companies_url, data={'name': 'Amazon'})
    assert response.status_code == 201
    assert response.data['name'] == 'Amazon'
    assert response.data['status'], 'Hiring'
    assert response.data['application_link'] == ''
    assert response.data['notes'] == ''


def test_post_company_with_layoffs_status_should_succeed(client) -> None:
    response = client.post(companies_url, data={'name': 'Amazon', 'status': 'Layoffs'})
    assert response.status_code == 201
    assert response.data['name'] == 'Amazon'
    assert response.data['status'] == 'Layoffs'


def test_post_company_with_wrong_status_should_return_error(client) -> None:
    response = client.post(companies_url, data={'name': 'Amazon', 'status': 'wrong'})
    response_data = json.loads(response.content)
    status_message = response_data['status'][0]
    assert response.status_code == 400

    assert response.data == {'status': ['"wrong" is not a valid choice.']}
    # or
    assert 'wrong' in status_message
    assert 'is not a valid choice.' in status_message


@pytest.mark.xfail(raises=AssertionError)
def test_should_be_ok_if_it_fails():
    assert 1 == 2


@pytest.mark.skip(reason='not implemented')
def test_should_be_skipped():
    assert 1 == 2
