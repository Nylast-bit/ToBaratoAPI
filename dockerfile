from python:3.11-slim

env PIP_DISABLE_PIP_VERSION_CHECK=1

ENV PYTHONUNBUFFERED=1


WORKDIR /app

COPY ./requirements.txt
RUN python -m venv venv

run /bin/bash -c "source venv/bin/activate"
run pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--reload","--host", "0.0.0.0", "--port", "8000"]