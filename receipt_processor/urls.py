"""
URL mappings for receipt_processor.
"""

from django.urls import path
from receipt_processor.views import ReceiptView, ReceiptPointsView

app_name = 'receipt-processor-challenge'

from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('receipts/process', ReceiptView.as_view(),
         name='receipt_processor.receipt'
        ),
    path('receipts/<str:receipt_id>/points/', ReceiptPointsView.as_view(),
         name='receipt_processor.points'
        ),
]
