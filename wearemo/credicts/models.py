from typing import List, Tuple

from django.db import models

class BaseModel(models.Model):

    #Datetime of creation
    created_at = models.DateTimeField(auto_now_add=True)
    #Datetime of last update
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        abstract = True


class Customers(BaseModel):

    """
        This model represent the information of the customers
    """

    STATUS_CUSTOMER_CHOICES: List[Tuple[int, str]] = [
        (0, 'Active'),
        (1, 'Inactive'),
    ]

    external_id = models.CharField(max_length=60)
    #Indicate the status of the customer
    status = models.SmallIntegerField(
        choices=STATUS_CUSTOMER_CHOICES,
        default=STATUS_CUSTOMER_CHOICES[0][0]
    )
    #Max mount that the customer can spend
    score = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    #Indicate the date that the customer is preapproved
    preapproved_at = models.DateTimeField(
        null=True,
        blank=True
    )

class Loans(BaseModel):

    """
        This model represent all the credict that have been approved for a customer
    """

    STATUS_LOAD_CHOICES: List[Tuple[int, str]] = [
        (0, 'Pending'),
        (1, 'Active'),
        (2, 'Rejected'),
        (3, 'Paid'),
    ]

    external_id = models.CharField(max_length=60)
    #Mount of the credict
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    #General information of the credict
    contract_version = models.CharField(max_length=30)
    #Status of the credict
    status = models.SmallIntegerField(
        choices=STATUS_LOAD_CHOICES,
        default=STATUS_LOAD_CHOICES[0][0]
    )
    #Maximun date that the credict can be paid
    maximum_payment_date = models.DateTimeField()
    taken_at = models.DateTimeField()
    #Total amount that the customer have to pay
    outstanding = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )
    #Customer ouwner of the credict
    customer = models.ForeignKey(
        Customers,
        on_delete=models.CASCADE
    )


class Payment(BaseModel):

    """
        This model represent all the payments that have been made for a customer
    """

    STATUS_PAYMENT_CHOICES: List[Tuple[int, str]] = [
        (0, 'Completed'),
        (1, 'Rejected')
    ]
    
    external_id = models.CharField(max_length=60)
    #Amount that the customer paid
    total_amount = models.DecimalField(
        max_digits=20,
        decimal_places=10
    )
    #Status of the payment
    status = models.SmallIntegerField(
        choices=STATUS_PAYMENT_CHOICES,
        default=STATUS_PAYMENT_CHOICES[0][0]
    )
    #Date that the payment was made
    paid_at = models.DateTimeField()
    #Customer ouwner of the payment
    customer = models.ForeignKey(
        Customers,
        on_delete=models.CASCADE
    )


class PaymentDetails(BaseModel):

    """
        This model represent all the payments details that have been made for a customer
    """

    #Total amount that the customer paid for a especific credict
    amount = models.DecimalField(
        max_digits=20,
        decimal_places=10
    )
    #Credict that the customer paid
    loan = models.ForeignKey(
        Loans,
        on_delete=models.CASCADE
    )
    #Payment that the customer made
    payment = models.ForeignKey(
        Payment,
        on_delete=models.CASCADE
    )


