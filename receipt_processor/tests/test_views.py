"""
All tests for views.py
"""
import json
from django.conf import settings

import ddt

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from receipt_processor.models import Item, ItemAssignmentToReceipt, Receipt

User = get_user_model()


@ddt.ddt
class ReceiptViewTests(TestCase):
    
    def setUp(self):
        self.receipt_data = {
            'retailer': 'Walgreens',
            'purchaseDate': '2022-01-02',
            'purchaseTime': '08:13',
            'total': '2.65',
            'items': [
                {'shortDescription': 'Pepsi - 12-oz', 'price': '1.25'},
                {'shortDescription': 'Dasani', 'price': '1.40'}
            ]
        }

    @ddt.data('retailer', 'purchaseDate', 'purchaseTime', 'total', 'items')
    def test_receipt_view_body_missing_values(self, attr_to_remove):
        del self.receipt_data[attr_to_remove]

        response = self.client.post(
            reverse('receipt_processor.receipt'),
            json.dumps(self.receipt_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    @ddt.data(
        # body is incorrectly formatted
        {
            'retailer': {
                'purchaseDate': '2022-01-02',
                'purchaseTime': '08:13',
                'total': '2.65',
            },
            'items': [
                {'shortDescription': 'Pepsi - 12-oz', 'price': '1.25'},
                {'shortDescription': 'Dasani', 'price': '1.40'}
            ]
        },
        {}  # body is empty
        )
    def test_receipt_view_invalid_body(self, receipt_data):
        response = self.client.post(
            reverse('receipt_processor.receipt'),
            json.dumps(receipt_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)

    # Test data = jsons in 'examples' folder & the README
    @ddt.data(
        ({
            'retailer': 'Walgreens',
            'purchaseDate': '2022-01-02',
            'purchaseTime': '08:13',
            'total': '2.65',
            'items': [
                {'shortDescription': 'Pepsi - 12-oz', 'price': '1.25'},
                {'shortDescription': 'Dasani', 'price': '1.40'}
            ]
        }, 15),
        ({
            'retailer': 'Target',
            'purchaseDate': '2022-01-02',
            'purchaseTime': '13:13',
            'total': '1.25',
            'items': [
                {'shortDescription': 'Pepsi - 12-oz', 'price': '1.25'}
            ]
        }, 31),
        ({
            'retailer': 'Target',
            'purchaseDate': '2022-01-01',
            'purchaseTime': '13:01',
            'items': [
                {
                'shortDescription': 'Mountain Dew 12PK',
                'price': '6.49'
                }, {
                'shortDescription': 'Emils Cheese Pizza',
                'price': '12.25'
                }, {
                'shortDescription': 'Knorr Creamy Chicken',
                'price': '1.26'
                }, {
                'shortDescription': 'Doritos Nacho Cheese',
                'price': '3.35'
                }, {
                'shortDescription': '   Klarbrunn 12-PK 12 FL OZ  ',
                'price': '12.00'
                }
            ],
            'total': '35.35'
        }, 28),
        ({
            'retailer': 'M&M Corner Market',
            'purchaseDate': '2022-03-20',
            'purchaseTime': '14:33',
            'items': [
                {
                'shortDescription': 'Gatorade',
                'price': '2.25'
                }, {
                'shortDescription': 'Gatorade',
                'price': '2.25'
                }, {
                'shortDescription': 'Gatorade',
                'price': '2.25'
                }, {
                'shortDescription': 'Gatorade',
                'price': '2.25'
                }
        ],
        'total': '9.00'
        }, 109)
    )
    @ddt.unpack
    def test_receipt_view_success(self, receipt_data, expected_points):
        response = self.client.post(
            reverse('receipt_processor.receipt'),
            json.dumps(receipt_data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        receipt_id = response.data['id']

        # receipt created as expected w/ correct values
        receipt = Receipt.objects.get(id=receipt_id)
        self.assertEqual(receipt.retailer, receipt_data['retailer'])
        self.assertEqual(receipt.purchase_date.strftime('%Y-%m-%d'), receipt_data['purchaseDate'])
        self.assertEqual(receipt.purchase_time.strftime('%H:%M'), receipt_data['purchaseTime'])
        self.assertEqual(str(receipt.total), receipt_data['total'])

        # items created and assigned as expected
        items = Item.objects.values_list()
        expected_items = receipt_data['items']
        item_assignments_to_receipt = ItemAssignmentToReceipt.objects.filter(receipt=receipt_id)
        for i in range(0, len(expected_items) - 1):
            item = items[i]
            expected_item = expected_items[i]
            assignment = item_assignments_to_receipt[i]

            self.assertEqual(item[1], expected_item['shortDescription'])  # Match item description
            self.assertEqual(str(item[2]), expected_item['price'])  # Match item price
            self.assertEqual(assignment.item.id, item[0])  # Match assignment to receipt

        # Points are correct
        self.assertEqual(receipt.points, expected_points)


@ddt.ddt
class ReceiptPointsViewTests(TestCase):

    def setUp(self):
        self.item = Item.objects.create(
            short_description='Pepsi - 12-oz',
            price='1.25'
        )
        self.receipt = Receipt.objects.create(
            retailer='Walgreens',
            purchase_date='2022-01-02',
            purchase_time='13:13',
            total='1.25',
            points=31,
        )
        ItemAssignmentToReceipt.objects.create(
            receipt=self.receipt,
            item=self.item,
        )

    # receipt does not exist, exception
    def test_receipt_does_not_exist(self):
        response = self.client.get(
            # Call the endpoint w/ the incorrect UUID
            reverse('receipt_processor.points', args=['ead122bd-3cef-40d3-8db1-835a75fef386']),
        )
        self.assertEqual(response.status_code, 404)

    # receipt returns points
    def test_get_points_for_receipt(self):
        response = self.client.get(
            reverse('receipt_processor.points', args=[self.receipt.id]),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['points'], 31)
