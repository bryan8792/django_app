# AGUAPAS Django

Panel administrativo para abonados, facturas mensuales, importación de Excel y campañas de WhatsApp.

## Instalación en Windows PowerShell

```powershell
cd django_app
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Abre `http://127.0.0.1:8000/` e inicia sesión.

## Flujo

1. Entra a `Importar Excel` y carga el archivo `.xlsx`.
2. El sistema crea o actualiza abonados por `CUENTA`.
3. Crea la factura del mes actual con `TOTAL`, `DEUDA` o `VALOR`.
4. Revisa y edita facturas desde el detalle del abonado.
5. Marca `consent_whatsapp` desde el admin para los contactos autorizados.
6. Crea una campaña y encola únicamente destinatarios con consentimiento.

El proyecto deja los mensajes en `MessageLog`. No inicia conversaciones sin consentimiento. Para producción, conecta un worker controlado a tu bot existente o usa WhatsApp Cloud API oficial; no pongas credenciales dentro del repositorio.

## API para que el bot entregue facturas

Agrega estas variables de entorno antes de iniciar Django:

```powershell
$env:BOT_API_KEY = 'genera-una-clave-larga-y-secreta'
$env:BOT_PUBLIC_URL = 'https://tu-dominio.example.com'
```

Consulta por cuenta:

```powershell
$headers = @{ 'X-Bot-API-Key' = $env:BOT_API_KEY }
Invoke-RestMethod 'http://127.0.0.1:8000/api/factura/?cuenta=24088' -Headers $headers
```

Consulta por cédula usando `/api/factura/?cedula=...`. Para recibir directamente el texto que puedes enviar por WhatsApp usa `/api/factura/mensaje/?cuenta=24088`.

En el bot, cuando el usuario escriba `factura`, solicita cuenta o cédula. Luego llama al endpoint con `X-Bot-API-Key`, envía el campo `message` y, si existe, envía también `invoice.invoice_url`. No publiques `BOT_API_KEY` en JavaScript del navegador ni en Git. En producción usa HTTPS y limita el endpoint por firewall o VPN si es posible.
