# app/utils.py
from datetime import datetime
import pytz
import random
from datetime import datetime, timedelta
from email.message import EmailMessage
from email_validator import validate_email, EmailNotValidError
from aiosmtplib import send


def now_bolivia():
    return datetime.now(pytz.timezone('America/La_Paz'))

def generar_codigo_otp() -> str:
    return str(random.randint(100000, 999999))


def obtener_expiracion_otp(minutos: int = 10) -> datetime:
    return datetime.utcnow() + timedelta(minutes=minutos)


def validar_correo(email: str) -> None:
    try:
        validate_email(email)
    except EmailNotValidError as e:
        raise ValueError("Correo electrónico inválido")


async def enviar_correo_otp(email: str, codigo: str):
    mensaje = EmailMessage()
    mensaje["From"] = "tu_correo@gmail.com"
    mensaje["To"] = email
    mensaje["Subject"] = "Código OTP"
    mensaje.set_content(f"Tu código de verificación es: {codigo}. Expira en 10 minutos.")

    await send(
        mensaje,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username="tu_correo@gmail.com",
        password="tu_contraseña_app"
    )