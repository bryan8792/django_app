from django.contrib import admin
from .models import Campaign, ImportBatch, Invoice, MessageLog, Subscriber
admin.site.register([Subscriber, Invoice, ImportBatch, Campaign, MessageLog])
