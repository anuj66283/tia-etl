FROM apache/airflow:slim-latest-python3.10

COPY requirements.txt .

RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN mkdir src

COPY ./src ./src
COPY utils.py .

