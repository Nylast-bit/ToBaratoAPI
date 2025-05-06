# app/utils.py
from datetime import datetime
import pytz

def now_bolivia():
    return datetime.now(pytz.timezone('America/La_Paz'))