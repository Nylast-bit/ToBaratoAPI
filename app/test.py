import sys
import os
import asyncio
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.utils import enviar_correo_otp

async def test_envio():
    await enviar_correo_otp("stalyn.fernandez27@gmail.com", "123456")

asyncio.run(test_envio())

input("Pulsa enter para salir")