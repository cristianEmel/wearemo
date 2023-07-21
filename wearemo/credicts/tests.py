# BEGIN: 1a2b3c4d5e6f
from typing import Dict, List

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from .models import Customers, Loans, Payment, PaymentDetails
from .serializers import CustomersSerializer


class CustomersViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        #Create user
        self.user: User = User.objects.create_user(
            username="test",
            password="test"
        )

        #Login
        url: str = reverse("api-token-auth")
        response = self.client.post(url, {"username": "test", "password": "test"}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['token'])

    def test_create_customer(self):

        """
            This method test the creation of a customer
        """

        data_customer: Dict[str, str] =  {
            "external_id": "1a2b3c4d5e6f",
            "status": 1,
            "score": 1000.00,
            "preapproved_at": "2020-01-01T00:00:00Z"
        }

        url: str = reverse("customers-list")
        response = self.client.post(url, data_customer)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Customers.objects.count(), 1)

    def test_create_customer_invalid_status(self):

        """
            This method test the creation of a customer with invalid status
        """
        external_id: str = "1a2b3c4d5e6f2"
        data_customer: Dict[str, str] =  {
            "external_id": external_id,
            "status": 2,
            "score": 1000.00,
            "preapproved_at": "2020-01-01T00:00:00Z"
        }
        url: str = reverse("customers-list")

        response = self.client.post(url, data_customer)
        self.assertEqual(Customers.objects.filter(external_id=external_id).first().status, 1)

    def test_create_customer_invalid_score(self):

        """
            This method test the creation of a customer with invalid status
        """

        data_customer: Dict[str, str] =  {
            "external_id": "1a2b3c4d5e6f",
            "status": 2,
            "score": -10,
            "preapproved_at": "2020-01-01T00:00:00Z"
        }
        url: str = reverse("customers-list")
        response = self.client.post(url, data_customer)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    

    def test_total_debt(self):

        #Create a customer
        customer: Customers = Customers.objects.create(
            external_id="1a2b3c4d5e6f",
            status=1,
            score=4000
        )
        #Create a loan
        loan: Loans = Loans.objects.create(
            external_id="1a2b3c4d5e6f",
            customer=customer,
            amount=3500,
            outstanding=3500,
        )

        url: str = reverse("customers-list")
        response = self.client.get(f'{url}{customer.id}/total_debt/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['external_id'], customer.external_id)
        self.assertEqual(response.data['score'], customer.score)
        self.assertEqual(response.data['total_debt'], loan.outstanding)
        self.assertEqual(response.data['available_amount'], customer.score - loan.outstanding)

class LoansViewSetTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        #Create user
        self.user: User = User.objects.create_user(
            username="test",
            password="test"
        )

        #Login
        url: str = reverse("api-token-auth")
        response = self.client.post(url, {"username": "test", "password": "test"}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['token'])

    def test_create_loan(self):
            
            """
                This method test the creation of a loan
            """
    
            #Create a customer
            customer: Customers = Customers.objects.create(
                external_id="1a2b3c4d5e6f",
                status=1,
                score=4000
            )
    
            data_loan: Dict[str, str] =  {
                "external_id": "1a2b3c4d5e6f",
                "amount": 3500,
                "contract_version": 1,
                "status": 1,
                "outstanding": 3500,
                "customer": customer.id
            }
    
            url: str = reverse("loans-list")
            response = self.client.post(url, data_loan)
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Loans.objects.count(), 1)

class PaymentViewSetTestCase(TestCase):

    def setUp(self):
        self.client = APIClient()

        #Create user
        self.user: User = User.objects.create_user(
            username="test",
            password="test"
        )

        #Login
        url: str = reverse("api-token-auth")
        response = self.client.post(url, {"username": "test", "password": "test"}, format='json')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + response.data['token'])

    def test_create_payment(self):
            
            """
                This method test the creation of a payment
            """
    
            #Create a customer
            customer: Customers = Customers.objects.create(
                external_id="1a2b3c4d5e6f",
                status=1,
                score=4000
            )
    
            #Create a loan
            loan: Loans = Loans.objects.create(
                external_id="1a2b3c4d5e6f",
                customer=customer,
                amount=3500,
                outstanding=3500,
            )
    
            data_payment: Dict[str, str] =  {
                "external_id": "1a2b3c4d5e6f",
                "total_amount": 3500,
                "paymentdetails": [
                    {
                        "loan": loan.id,
                        "amount": 3500
                    }
                ],
                "customer": customer.id
            }
    
            url: str = reverse("add_payment")
            response = self.client.post(url, data_payment, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Loans.objects.get(id=loan.id).outstanding, 0)
            self.assertEqual(Payment.objects.all().count(), 1)
            self.assertEqual(PaymentDetails.objects.all().count(), 1)

    def test_reject_payment(self):
         
        """
                This method test the rejection of a payment
        """
    
        #Create a customer
        customer: Customers = Customers.objects.create(
            external_id="1a2b3c4d5e6f",
            status=1,
            score=4000
        )

        #Create a loan
        loan: Loans = Loans.objects.create(
            external_id="1a2b3c4d5e6f",
            customer=customer,
            amount=3500,
            outstanding=3500,
        )

        data_payment: Dict[str, str] =  {
            "external_id": "1a2b3c4d5e6f",
            "total_amount": 3500,
            "paymentdetails": [
                {
                    "loan": loan.id,
                    "amount": 3500
                }
            ],
            "customer": customer.id
        }

        url: str = reverse("add_payment")
        response = self.client.post(url, data_payment, format='json')

        data_payment: Dict[str, str] =  {
            "payment": Payment.objects.all().first().id
        }

        url: str = reverse("rejecte_payment")
        response = self.client.post(url, data_payment, format='json')

        self.assertEqual(Loans.objects.get(id=loan.id).outstanding, 3500)

        response = self.client.post(url, data_payment, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)