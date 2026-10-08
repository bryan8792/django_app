from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import Campaign, ImportBatch, Invoice, Subscriber

User = get_user_model()

class StaffUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']

class StaffUserUpdateForm(forms.ModelForm):
    password = forms.CharField(required=False, widget=forms.PasswordInput, help_text='Déjalo vacío para conservar la contraseña actual.')
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_staff', 'is_active']

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user

class ExcelImportForm(forms.Form):
    file = forms.FileField(label='Archivo Excel (.xlsx)')
    def clean_file(self):
        f = self.cleaned_data['file']
        if not f.name.lower().endswith('.xlsx'): raise forms.ValidationError('Solo se permiten archivos .xlsx')
        if f.size > 10 * 1024 * 1024: raise forms.ValidationError('El archivo no puede superar 10 MB')
        return f

class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['period','previous_reading','current_reading','amount','due_date','status']
        widgets = {'period': forms.DateInput(attrs={'type':'date'}), 'due_date': forms.DateInput(attrs={'type':'date'})}

class CampaignForm(forms.ModelForm):
    DEFAULT_MESSAGE = ('Estimado(a) {nombre},\n'
        'Detalle de su factura de agua potable correspondiente a {periodo}.\n'
        'Cuenta: {cuenta}\n'
        'Propietario: {nombre}\n'
        'Total a pagar: $ {total}\n'
        'Le solicitamos acercarse a nuestras oficinas para regularizar su situación. '
        'Si ya realizó el pago, ignore este mensaje.\n'
        'Atentamente,\nAGUAPAS EP - BOT\n'
        'Empresa Pública de Agua, Alcantarillado y Aseo de Pasaje')
    MONTHS = [(1, 'Enero'), (2, 'Febrero'), (3, 'Marzo'), (4, 'Abril'), (5, 'Mayo'), (6, 'Junio'), (7, 'Julio'), (8, 'Agosto'), (9, 'Septiembre'), (10, 'Octubre'), (11, 'Noviembre'), (12, 'Diciembre')]
    period = forms.TypedChoiceField(choices=MONTHS, coerce=int, label='Mes de la planilla')
    send_mode = forms.ChoiceField(choices=[('now', 'Enviar ahora'), ('schedule', 'Programar envío')], initial='schedule', widget=forms.RadioSelect, label='Momento del envío')
    import_batch = forms.ModelChoiceField(queryset=ImportBatch.objects.none(), required=True, label='Archivo de usuarios')
    recipients = forms.ModelMultipleChoiceField(
        queryset=Subscriber.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label='Destinatarios autorizados',
    )

    def clean_period(self):
        from datetime import date
        return date.today().replace(month=int(self.cleaned_data['period']), day=1)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.instance.pk and not self.data:
            self.fields['message_template'].initial = self.DEFAULT_MESSAGE
        batches = ImportBatch.objects.order_by('-created_at')
        self.fields['import_batch'].queryset = batches
        selected_batch = self.data.get('import_batch') or (self.instance.import_batch_id if self.instance.pk else batches.values_list('pk', flat=True).first())
        if selected_batch:
            self.fields['import_batch'].initial = selected_batch
            recipients = Subscriber.objects.filter(import_batch_id=selected_batch, active=True).exclude(phone='').order_by('full_name')
            if not recipients.exists():
                recipients = Subscriber.objects.filter(active=True).exclude(phone='').order_by('full_name')
            self.fields['recipients'].queryset = recipients

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('send_mode') == 'schedule' and not cleaned.get('scheduled_for'):
            self.add_error('scheduled_for', 'Selecciona la fecha y hora para programar el envío.')
        if not cleaned.get('message_template'):
            self.add_error('message_template', 'Escribe el mensaje que se enviará.')
        batch = cleaned.get('import_batch')
        recipients = cleaned.get('recipients')
        if batch and not recipients:
            cleaned['recipients'] = Subscriber.objects.filter(import_batch=batch, active=True).exclude(phone='').order_by('full_name')
        return cleaned

    class Meta:
        model = Campaign
        fields = ['name','import_batch','period','message_template','scheduled_for','send_mode']
        widgets = {'period': forms.DateInput(attrs={'type':'date'}), 'scheduled_for': forms.DateTimeInput(attrs={'type':'datetime-local'})}
