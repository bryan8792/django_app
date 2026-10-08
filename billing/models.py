from django.conf import settings
from django.db import models

class Subscriber(models.Model):
    account_number = models.CharField('Cuenta', max_length=60, unique=True)
    import_batch = models.ForeignKey('ImportBatch', null=True, blank=True, on_delete=models.SET_NULL, related_name='subscribers')
    national_id = models.CharField('Cédula', max_length=30, blank=True)
    full_name = models.CharField('Abonado', max_length=180)
    phone = models.CharField('WhatsApp', max_length=30, blank=True)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=80, blank=True)
    sequence = models.CharField(max_length=30, blank=True)
    client_code = models.CharField(max_length=60, blank=True)
    meter_number = models.CharField(max_length=60, blank=True)
    total_letters = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    previous_reading = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_reading = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    active = models.BooleanField(default=True)
    consent_whatsapp = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self): return f'{self.account_number} - {self.full_name}'

class Invoice(models.Model):
    STATUS = [('pending','Pendiente'),('paid','Pagada'),('cancelled','Anulada')]
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE, related_name='invoices')
    period = models.DateField(help_text='Usa el primer día del mes')
    previous_reading = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    current_reading = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta: unique_together = ('subscriber','period'); ordering = ['-period','subscriber__full_name']

class ImportBatch(models.Model):
    file = models.FileField(upload_to='imports/')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    rows_imported = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'{self.file.name.split("/")[-1]} · {self.rows_imported} usuarios'

class Campaign(models.Model):
    name = models.CharField(max_length=160)
    import_batch = models.ForeignKey('ImportBatch', null=True, blank=True, on_delete=models.SET_NULL, related_name='campaigns')
    period = models.DateField(null=True, blank=True)
    message_template = models.TextField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=30, default='draft')

class MessageLog(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='messages')
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    status = models.CharField(max_length=30, default='queued')
    sent_at = models.DateTimeField(null=True, blank=True)
    error = models.TextField(blank=True)
