from rest_framework import serializers

class DocRejectedPaymentDataSerializer(serializers.Serializer):
    payment: int = serializers.IntegerField(min_value=1)

class DocPaymentDetailsSerializer(serializers.Serializer):
    loan: int = serializers.IntegerField(min_value=1)
    amount: float = serializers.FloatField(min_value=0)

class DocCreatePaymentDataSerializer(serializers.Serializer):
    customer: int = serializers.IntegerField(min_value=1)
    total_amount: float = serializers.FloatField(min_value=0)
    external_id: str = serializers.CharField(max_length=60)
    total_amount: float = serializers.FloatField(min_value=0)
    paymentdetails: list = serializers.ListField(
        child=DocPaymentDetailsSerializer()
    )