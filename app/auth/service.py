from app.models.models import Usuario
from datetime import datetime, timedelta
from dotenv import load_dotenv
import jwt 
import uuid
import os
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

class UsuarioService:
    async def getUsuarioByEmail(self, correo: str, session: AsyncSession):
        statement = select(Usuario).where(Usuario.Correo == correo)

        result = await session.execute(statement)

        Usuario = result.first()

        return Usuario
    
    async def usuarioExiste(self, correo: str, session: AsyncSession):
        user = await self.getUsuarioByEmail(correo, session)

        if user is None:
            return False
        
        else:
            return True