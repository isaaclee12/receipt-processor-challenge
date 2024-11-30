from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from receipt_processor.models import Receipt

from datetime import datetime
import json

class ReceiptView(APIView):
    """
    Endpoint for getting attempt storing the data for a receipt.

    Supports:
        HTTP POST:
            Creates a new Receipt
    """

    permission_classes = (AllowAny, )
    http_method_names = ['post', 'head']

    def post(self, request):
        request_body = json.loads(request.body)
        retailer = request_body.get('retailer')
        purchase_date = request_body.get('purchaseDate')
        purchase_time = request_body.get('purchaseTime')
        total = request_body.get('total')
        items = request_body.get('items')

        # Data cleaning
        year, month, day = [int(x) for x in purchase_date.split("-")]
        hour, minute = [int(x) for x in purchase_time.split(":")]
        purchase_datetime = datetime(year=year, month=month, day=day, hour=hour, minute=minute)
        total = float(total)

        print("\n\n\nITEMS", items)
        # for item in items:

        # Create a Receipt, (or get if it already exists), extract the id.
        receipt, _ = Receipt.objects.get_or_create(
            retailer=retailer,
            purchase_datetime=purchase_datetime,
            total=total,
            items=items,
        )

        print("RECEIPT", receipt)

        # Return id
        return Response(data={"id": receipt.id}, status=200)


class ReceiptPointsView(APIView):
    def get(self):
        # If a receipt exists for the ID that has the point value, return the points.
        # Else, generate the point value and return it.
        return Response()