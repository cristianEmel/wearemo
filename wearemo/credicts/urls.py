from django.urls import include, path
from rest_framework import routers

from .views import (CustomersViewSet, LoansViewSet,
                    create_payment, rejected_payment)

router = routers.DefaultRouter()
router.register(r'customer', CustomersViewSet)
router.register(r'loan', LoansViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("payment/add", create_payment, name="add_payment"),
    path("payment/rejecte", rejected_payment, name="rejecte_payment"),
]