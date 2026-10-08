from decimal import Decimal
import os
import secrets
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from .models import Invoice, Subscriber


def _authorized(request):
    expected = os.getenv('BOT_API_KEY', '').strip()
    received = request.headers.get('X-Bot-API-Key', '').strip()
    return bool(expected) and bool(received) and secrets.compare_digest(received, expected)


@csrf_exempt
def bot_invoice(request):
    if request.method != 'GET':
        return JsonResponse({'ok': False, 'error': 'method_not_allowed'}, status=405)
    if not _authorized(request):
        return JsonResponse({'ok': False, 'error': 'unauthorized'}, status=401)

    account = request.GET.get('cuenta', '').strip()
    national_id = request.GET.get('cedula', '').strip()
    if not account and not national_id:
        return JsonResponse({'ok': False, 'error': 'debes_indicar_cuenta_o_cedula'}, status=400)

    filters = {'account_number': account} if account else {'national_id': national_id}
    subscriber = Subscriber.objects.filter(active=True, **filters).first()
    if not subscriber:
        return JsonResponse({'ok': False, 'error': 'abonado_no_encontrado'}, status=404)

    invoice = subscriber.invoices.order_by('-period', '-created_at').first()
    if not invoice:
        return JsonResponse({'ok': False, 'error': 'factura_no_encontrada'}, status=404)

    public_url = os.getenv('BOT_PUBLIC_URL', '').rstrip('/')
    invoice_url = f'{public_url}/facturas/{invoice.pk}/' if public_url else None
    return JsonResponse({
        'ok': True,
        'abonado': {
            'nombre': subscriber.full_name,
            'cuenta': subscriber.account_number,
            'cedula': subscriber.national_id,
            'telefono': subscriber.phone,
            'direccion': subscriber.address,
        },
        'factura': {
            'id': invoice.pk,
            'periodo': invoice.period.strftime('%Y-%m'),
            'total': str(invoice.amount.quantize(Decimal('0.01'))),
            'estado': invoice.get_status_display(),
            'vencimiento': invoice.due_date.isoformat() if invoice.due_date else None,
            'lectura_anterior': str(invoice.previous_reading),
            'lectura_actual': str(invoice.current_reading),
            'invoice_url': invoice_url,
        },
    })


def bot_invoice_message(request):
    response = bot_invoice(request)
    if response.status_code != 200:
        return response
    data = response.json()
    invoice = data['factura']
    person = data['abonado']
    text = (
        f"Factura {invoice['periodo']}\\n"
        f"Abonado: {person['nombre']}\\n"
        f"Cuenta: {person['cuenta']}\\n"
        f"Total: ${invoice['total']}\\n"
        f"Estado: {invoice['estado']}"
    )
    if invoice['vencimiento']:
        text += f"\\nVencimiento: {invoice['vencimiento']}"
    if invoice['invoice_url']:
        text += f"\\nVer factura: {invoice['invoice_url']}"
    return JsonResponse({'ok': True, 'message': text, 'invoice': invoice, 'abonado': person})

