from rest_framework import serializers
from .models import Customers, Loans, Payment, PaymentDetails
from typing import List, Dict, Any
from django.db import models
from datetime import datetime


class CustomersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customers
        fields: List[str] = [
            "id",
            "external_id",
            "status",
            "score",
            "preapproved_at"
        ]
        read_only_fields: List[str] = ["outstanding"]

    
    def validate_status(self, value: int) -> int:

        """
            This method validate the status of the customer

            :param value: Status of the customer
            :type value: int

            :return: Status of the customer
            :rtype: int
        """

        #Validate if the instance is being created
        if self.instance is None:
            #When a Customer is created, the status must be 0
            value: int = 1

        return value
    
class LoansSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loans
        fields: List[str] = [
            "id",
            "external_id",
            "amount",
            "contract_version",
            "status",
            "outstanding",
            "customer"
        ]

    def validate_amount(self, amount: int) -> float:
            
        """
            This method validate the amount of the loan

            :param amount: Amount of the loan
            :type amount: float

            :return: Amount of the loan
            :rtype: float
        """
        #Total mount in credict of the customer
        customer_id: int = self.initial_data.get('customer') or self.instance.customer.id
        customer: Customers = Customers.objects.get(id=customer_id)
        total_amount: float = Loans.objects.filter(
            customer=customer,
            status__in=[0, 1]
        ).aggregate(total_amount=models.Sum('amount')).get('total_amount', 0)
        total_amount: float = total_amount if total_amount else 0

        #Validate if the amount is greater than the available amount
        if total_amount + amount > customer.score:
            raise serializers.ValidationError("Dont cant create a loan with this amount")
        
        return amount
            
    def validate(self, attrs) -> Dict[str, Any]:

        """
            This method validate the data of the loan

            :param attrs: Data of the loan
            :type attrs: dict

            :return: Data of the loan
            :rtype: dict
        """

        #Validate if the instance is being created
        if self.instance is None:

            #Validate the status when the loan will be created
            status: int = attrs.get('status')
            if status == 2:
                attrs["taken_at"] = datetime.now()
            elif status == 3:
                raise serializers.ValidationError("A loan cant be created how rejected")
            elif status == 4:
                raise serializers.ValidationError("A loan cant be created how paid")
            
            #When a Loan is created, the outstanding must be equeal to the amount
            attrs["outstanding"] = attrs["amount"]
            
        else:

            #Validate the status when the loan exist
            status: int = attrs.get('status')
            if status == 2 and self.instance.status == 1:
                attrs["taken_at"] = datetime.now()
            elif status == 3 and self.instance.status != 1:
                raise serializers.ValidationError("A loan can only be rejected when it is pending")
            elif status == 4:
                raise serializers.ValidationError("Dont cant update a loan how paid directly, use the payment endpoint")
            
            if status in [1,2] and self.instance.status in [3,4]:
                raise serializers.ValidationError("A loan cant be updated how Pending or Active after be rejected or paid")

            #Validate that the outstanding cant be updated directly
            if "outstanding" in attrs:
                del attrs["outstanding"]
                
            #Validate that the amount cant be updated directly
            if "amount" in attrs:
                del attrs["amount"]

        return super().validate(attrs)

class PaymentDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentDetails
        fields: List[str] = [
            "id",
            "amount",
            "loan"
        ]

class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields: List[str] = [
            "id",
            "total_amount",
            "status",
            "paid_at",
            "customer"
        ]
    
    def validate_total_amount(self, total_amount) -> float:

        """
            This method validate the total amount of the payment

            :param total_amount: Total amount of the payment
            :type total_amount: float

            :return: Total amount of the payment
            :rtype: float
        """

        self.validate_paymentdetails(self.initial_data.get('paymentdetails'))

        #Validate that the total amount is equal to the sum of the amount of the payment details
        if total_amount != sum([payment_detail.get('amount') for payment_detail in self.initial_data.get('paymentdetails')]):
            raise serializers.ValidationError("The total amount is not equal to the sum of the amount of the payment details")
        
        return total_amount





