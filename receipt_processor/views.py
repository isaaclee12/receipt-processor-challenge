"""
Views for receipt_processor
"""
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from receipt_processor.models import Item, ItemAssignmentToReceipt, Receipt

from datetime import date, time
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
        try:
            request_body = json.loads(request.body)
            retailer = request_body['retailer']
            purchase_date = request_body['purchaseDate']
            purchase_time = request_body['purchaseTime']
            total = request_body['total']
            items = request_body['items']
        except KeyError as e:
            return Response(f'Request receipt data invalid, missing data for the following attribute: {e}', status=400)
        except Exception as e:
            return Response(f'Request receipt data invalid, threw the following exception: {e}', status=400)

        # Data cleaning
        year, month, day = [int(x) for x in purchase_date.split('-')]
        hour, minute = [int(x) for x in purchase_time.split(':')]

        purchase_date = date(year=year, month=month, day=day)
        purchase_time = time(hour=hour, minute=minute)
        total = float(total)

        # Create a Receipt, (or get if it already exists), extract the id.
        receipt, _ = Receipt.objects.get_or_create(
            retailer=retailer,
            purchase_date=purchase_date,
            purchase_time=purchase_time,
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
        amount_item_pairs = math.floor(len(items) / 2)
        points += amount_item_pairs * 5

        # 6 points if the day in the purchase date is odd.
        if day % 2 != 0:
            points += 6

        # 10 points if the time of purchase is after 2:00pm and before 4:00pm.
        two_pm = time(hour=14, minute=0, second=0, microsecond=0, tzinfo=None, fold=0)
        four_pm = time(hour=16, minute=0, second=0, microsecond=0, tzinfo=None, fold=0)
        purchase_between_two_and_four = two_pm <= purchase_time < four_pm
        if purchase_between_two_and_four:
            points += 10

        # Get or create the items
        # Also count the points for the item descriptions
        for item in items:
            short_description = item.get('shortDescription')
            price = item.get('price')
            price = float(price)
            # Note: we need a unique item object for each item to get the counts right
            item_object = Item.objects.create(
                    short_description=short_description,
                    price=price,
                )

            # If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer.
            # The result is the number of points earned.
            trimmed_item_description = short_description.strip()
            if len(trimmed_item_description) % 3 == 0:
                points += math.ceil(price * 0.2)

            ItemAssignmentToReceipt.objects.create(
                item=item_object,
                receipt=receipt,
            )

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
    http_method_names = ['get', 'head']

    def get(self, request, receipt_id):
        try:
            receipt = Receipt.objects.get(id=receipt_id)
        except Exception as e:
            return Response(f'Receipt could not be found for id {receipt_id}, threw the following exception: {e}', status=404)

        points = receipt.points
        return Response(data={'points': points}, status=200)
