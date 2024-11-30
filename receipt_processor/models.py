from django.db import models
from datetime import datetime
import uuid

class Item(models.Model):
    short_description = models.CharField(max_length=100, blank=False, null=False, default='')
    price = models.DecimalField(max_digits=20, decimal_places=2, blank=False, null=False, default=0)

class Receipt(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    retailer = models.CharField(max_length=30, blank=False, null=False)
    purchase_datetime = models.DateTimeField(blank=False, null=False)
    total = models.DecimalField(max_digits=20, decimal_places=2, blank=False, null=False)
    points = models.IntegerField(default=0)
    # create a join table with foreign keys to Receipt and Item
    items = models.ManyToManyField(Item, through='ItemAssignmentToReceipt')

class ItemAssignmentToReceipt(models.Model):
    receipt = models.ForeignKey(Receipt, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
