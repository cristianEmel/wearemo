from typing import Any, Dict, List

from django.db import models
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .doc_serializer import (DocCreatePaymentDataSerializer,
                             DocRejectedPaymentDataSerializer)
from .models import Customers, Loans, Payment, PaymentDetails
from .serializers import (CustomersSerializer, LoansSerializer,
                          PaymentSerializer)


def _total_debt(customer: Customers) -> float:

        """
            This method return the total debt of a customer

            :param customer: Customer object
            :type customer: Customers

            :return: Total debt of the customer
            :rtype: float
        """

        #Calculate the total debt
        total_debt: float = Loans.objects.filter(
            customer=customer,
            status__in=[0, 1]
        ).aggregate(total_debt=models.Sum('outstanding')).get('total_debt', 0)

        return total_debt if total_debt else 0

class CustomersViewSet(viewsets.ModelViewSet):
    queryset = Customers.objects.all()
    serializer_class = CustomersSerializer

    permission_classes = (IsAuthenticated,)

    @action(detail=True, methods=['get'])
    def payments(self, request, pk) -> Response:

        """
            This method return all the payments of a customer
        
            :param request: Request object
            :type request: Request
            :param pk: Primary key of the customer
            :type pk: int

            :return: Response object
            :rtype: Response
        """

        #Get the customer
        customer: Customers = self.get_object()
        #Get all the payments of the customer
        payments: Payment = Payment.objects.filter(customer=customer)
        #Serialize the payments
        payments_serializer: PaymentSerializer = PaymentSerializer(payments, many=True)

        return Response(
            payments_serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def loads(self, request, pk) -> Response:

        """
            This method return all the loans of a customer

            :param request: Request object
            :type request: Request
            :param pk: Primary key of the customer
            :type pk: int

            :return: Response object
            :rtype: Response
        """

        #Get the customer
        customer: Customers = self.get_object()
        #Get all the loans of the customer
        loans: Loans = Loans.objects.filter(customer=customer)
        #Serialize the loans
        loans_serializer: LoansSerializer = LoansSerializer(loans, many=True)

        return Response(
            loans_serializer.data,
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=['get'])
    def total_debt(self, request, pk) -> Response:

        """
            This method return the total debt of a customer

            :param request: Request object
            :type request: Request
            :param pk: Primary key of the customer
            :type pk: int

            :return: Response object
            :rtype: Response
        """

        #Get the customer
        customer: Customers = self.get_object()
        #Calculate the total debt
        total_debt: float = _total_debt(customer)

        #Calculate the available amount
        score: float = customer.score
        available_amount: float = score - total_debt

        return Response(
            {
                "external_id": customer.external_id,
                "score": score,
                "available_amount": available_amount,
                "total_debt": total_debt
            },
            status=status.HTTP_200_OK
        )
    
class LoansViewSet(viewsets.ModelViewSet):
    queryset = Loans.objects.all()
    serializer_class = LoansSerializer

    permission_classes = (IsAuthenticated,)


@swagger_auto_schema(
    methods=['post'],
    request_body=DocRejectedPaymentDataSerializer,
    responses={})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def rejected_payment(request) -> Response:

    """
        This method reject a payment
        Aditional, update the information of the loans
    """
    payment_pk: int = request.data['payment']
    payment_instance: Payment = Payment.objects.get(pk=payment_pk)

    if payment_instance.status == 1:
        return Response(
            {
                "message": "The payment was rejected previously"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    payment_instance.status: int = 1
    payment_instance.save()

    #Get payment details
    payment_details: PaymentDetails = PaymentDetails.objects.filter(payment=payment_instance)
    for detail in payment_details:
        loan: Loans = detail.loan
        loan.outstanding: float = loan.outstanding + detail.amount
        loan.status: int = 1
        loan.save()

    return Response(
        status=status.HTTP_200_OK
    )

@swagger_auto_schema(
    methods=['post'],
    request_body=DocCreatePaymentDataSerializer,
    responses={})
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_payment(request) -> Response: 

    """
        This method create a payment with all the details
        Adicional, update the debict of the loan
    """

    #Get the customer
    customer: Customers = Customers.objects.get(pk=request.data['customer'])
    #Get the total debt of the customer
    total_debt: float = _total_debt(customer)

    response_json: Dict[str, str] = {}
    response_status: int = status.HTTP_201_CREATED
    failed: bool = False

    #If the customer does not have any debt, dont create the payment
    if total_debt == 0:
        response_json: Dict[str, str] = {
            "message": "The customer does not have any debt"
        }
        response_status: int = status.HTTP_400_BAD_REQUEST

    #Validate if the amount of the payment is greater than the total debt, dont create the payment
    elif float(request.data['total_amount']) > total_debt:
        response_json: Dict[str, str] = {
            "message": "The amount of the payment is greater than the total debt"
        }
        response_status: int = status.HTTP_400_BAD_REQUEST

    else:

        #Get all the active loans of the customer
        loans_of_customer: Loans = Loans.objects.filter(
            customer=customer,
            status__in=[0, 1]
        )
        loans_of_customer: Dict[int, Loans] = { loan.id:loan for loan in loans_of_customer}

        #Validate that all the payments details are correct
        #All the loan must exist
        #The amount of the payment must be less than the outstanding of the loan
        for payment_detail in request.data['paymentdetails']:
            loan_id: int = payment_detail['loan']
            loan: Loans = loans_of_customer.get(loan_id)
            #The loan must exist
            if not loan:
                response_json: Dict[str, str] = {
                    "message": f"The loan {loan_id} does not exist"
                }
                response_status: int = status.HTTP_400_BAD_REQUEST
                failed: bool = True

            #The amount of the payment must be less or equal than the outstanding of the loan
            if payment_detail['amount'] > loan.outstanding:

                response_json: Dict[str, str] = {
                    "message": f"The amount of the payment is greater than the outstanding of the loan {loan_id}"
                }
                response_status: int = status.HTTP_400_BAD_REQUEST
                failed: bool = True

        if not failed:

            #Create the payment
            payment_instance: Payment = Payment.objects.create(
                external_id=request.data['external_id'],
                total_amount=request.data['total_amount'],
                customer=customer
            )

            #For all the payment details, create the payment detail and update the outstanding of the loan
            for payment_detail in request.data['paymentdetails']:

                loan: Loans = loans_of_customer[payment_detail['loan']]
                payment_detail_amount: float = payment_detail['amount']

                PaymentDetails.objects.create(
                    amount=payment_detail_amount,
                    loan=loan,
                    payment=payment_instance
                )
                
                #Reduce the outstanding of the loan
                loan.outstanding = loan.outstanding - payment_detail_amount
                #If the outstanding of the loan is 0, update the status of the loan
                if loan.outstanding == 0:
                    loan.status = 4
                loan.save()

    return Response(
        response_json,
        status=response_status
    )