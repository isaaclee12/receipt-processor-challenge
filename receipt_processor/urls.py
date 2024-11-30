"""
URL mappings for edX Proctoring Server.
"""

from django.conf import settings
from django.urls import path
from receipt_processor.views import ReceiptView, ReceiptPointsView

app_name = 'receipt-processor-challenge'

from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('receipts/process', ReceiptView.as_view(),
         name='reciept_processor.receipt'
        ),
    path('receipts/<str:receipt_id>/points/', ReceiptPointsView.as_view(),
         name='reciept_processor.receipt'
        ),
]
