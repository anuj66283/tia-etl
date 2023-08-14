from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

#needed to import files from internal folders
import sys, os
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(src_dir)

from src.transform import sep_data
from src.extract import put_data
from src.load import main

bucket = os.environ['BUCKET_NAME']

#arguments for our dag
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 8, 10, 1, 42),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}


dag = DAG(
    'etl_pipeline',
    default_args=default_args,
    description='ETL pipeline with Airflow',
    schedule=timedelta(minutes=30), #runs every 30 min interval
)

extract_task = PythonOperator(
    task_id='extract',
    python_callable=put_data,
    dag=dag,
    op_args=[bucket]
)

transform_task = PythonOperator(
    task_id='transform',
    python_callable=sep_data,
    dag=dag,
    op_args=[bucket]
)

load_task = PythonOperator(
    task_id='load',
    python_callable=main,
    dag=dag
)


extract_task >> transform_task >> load_task