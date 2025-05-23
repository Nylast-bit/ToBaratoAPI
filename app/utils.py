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

def render_template_con_codigo(codigo: str) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
      <meta charset="UTF-8" />
      <title>Tu código OTP</title>
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px;">

      <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); overflow: hidden;">

        <!-- Encabezado con fondo azul -->
        <div style="background-color: #33618d; padding: 30px 20px; text-align: center;">
          <img src="logo.png" alt="ToBarato Logo" style="max-width: 120px; margin-bottom: 10px;" />
          <h2 style="color: white; margin: 0;">Verifica tu correo</h2>
        </div>

        <!-- Contenido -->
        <div style="padding: 30px 20px; text-align: center;">
          <p style="font-size: 16px; color: #333;">Hola,</p>
          <p style="font-size: 16px; color: #333;">
            Gracias por registrarte en <strong>ToBarato</strong>. Usa el siguiente código para verificar tu correo:
          </p>

          <div style="margin: 30px auto; display: inline-block; background-color: #f5f5f5; padding: 20px 30px; border-radius: 6px; border: 2px dashed #f3732a;">
            <p style="font-size: 28px; letter-spacing: 4px; color: #f3732a; margin: 0;"><strong>{codigo}</strong></p>
          </div>

          <p style="font-size: 14px; color: #666; margin-top: 20px;">
            Este código expirará en 10 minutos.
          </p>
        </div>

        <!-- Pie -->
        <div style="background-color: #f4f4f4; padding: 15px 20px; text-align: center; font-size: 12px; color: #999;">
          © 2025 ToBarato. Todos los derechos reservados.
        </div>

      </div>
    </body>
    </html>
    """


async def enviar_correo_otp(email: str, codigo: str):
    html = render_template_con_codigo(codigo)  # crea una función para inyectar el código

    mensaje = EmailMessage()    
    mensaje["From"] = "tobaratodo@gmail.com"
    mensaje["To"] = email
    mensaje["Subject"] = "Código OTP"
    mensaje.set_content("Tu código de verificación es: " + codigo)  # fallback texto plano
    mensaje.add_alternative(html, subtype="html")



    await send(
        mensaje,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username="tobaratodo@gmail.com",
        password="dmsv hzmk dbne pfxk" 
    )