# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster
WORKDIR /AccountingFastAPI
COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "81"]