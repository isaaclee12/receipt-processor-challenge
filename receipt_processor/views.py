from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from receipt_processor.models import Item, ItemAssignmentToReceipt, Receipt

from datetime import datetime, time
import json
import math

class ReceiptView(APIView):
    """
    Endpoint for storing the data for a receipt.

    Supports:
        HTTP POST:
            Creates a new Receipt
    """

    permission_classes = (AllowAny,)
    http_method_names = ['post', 'head']

    def post(self, request):
        request_body = json.loads(request.body)
        retailer = request_body.get('retailer')
        purchase_date = request_body.get('purchaseDate')
        purchase_time = request_body.get('purchaseTime')
        total = request_body.get('total')
        items = request_body.get('items')

        # Data cleaning
        year, month, day = [int(x) for x in purchase_date.split('-')]
        hour, minute = [int(x) for x in purchase_time.split(':')]
        purchase_datetime = datetime(year=year, month=month, day=day, hour=hour, minute=minute)
        total = float(total)

        # Create a Receipt, (or get if it already exists), extract the id.
        receipt, _ = Receipt.objects.get_or_create(
            retailer=retailer,
            purchase_datetime=purchase_datetime,
            total=total,
        )

        # Start counting points
        points = 0

        # One point for every alphanumeric character in the retailer name.
        numbers = sum(ch.isdigit() for ch in retailer)
        letters = sum(ch.isalpha() for ch in retailer)
        points += numbers + letters

        # 50 points if the total is a round dollar amount with no cents.
        if total.is_integer():
            points += 50

        # 25 points if the total is a multiple of 0.25.
        if total % 0.25 == 0:
            points += 25

        # 5 points for every two items on the receipt.
        amount_item_pairs = math.floor(len(items)/2)
        points += amount_item_pairs * 5

        # 6 points if the day in the purchase date is odd.
        if day % 2 != 0:
            points += 6

        # 10 points if the time of purchase is after 2:00pm and before 4:00pm.
        two_pm = time(hour=14, minute=0, second=0, microsecond=0, tzinfo=None, fold=0)
        four_pm = time(hour=16, minute=0, second=0, microsecond=0, tzinfo=None, fold=0)
        purchase_between_two_and_four = two_pm <= purchase_datetime.time() < four_pm
        if purchase_between_two_and_four:
            points += 10

        # Get or create the items
        # Also count the points for the item descriptions
        for item in items:
            short_description = item.get('shortDescription')
            price = item.get('price')
            price = float(price)
            item_object, _ = Item.objects.get_or_create(
                    short_description=short_description,
                    price=price,
                )

            # If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer.
            # The result is the number of points earned.
            trimmed_item_description = short_description.strip()
            if len(trimmed_item_description) % 3 == 0:
                points += math.ceil(price * 0.2)

            ItemAssignmentToReceipt.objects.get_or_create(
                item=item_object,
                receipt=receipt,
            )

        print("POINTS:", points)
        receipt.points = points
        receipt.save()

        return Response(data={'id': receipt.id}, status=200)


class ReceiptPointsView(APIView):
    """
    Endpoint for getting the points for a receipt.

    Supports:
        HTTP GET:
            Get the points for a Receipt
    """

    permission_classes = (AllowAny,)
    http_method_names = ['post', 'head']

    def get(self, receipt_id):
        receipt, _ = Receipt.objects.get(receipt=receipt_id)
        points = receipt.points
        return Response(data={'points': points}, status=200)
