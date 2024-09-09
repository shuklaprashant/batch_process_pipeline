from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import sys
sys.path.append('/opt/airflow/dags')

# Import the task1 function from the task1.py file
# from task1 import task1_function

from src import upload_to_target

# Default arguments for the DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 9, 1),
    'retries': 1,
}

# Define the DAG
with DAG('dag_task2',
         default_args=default_args,
         schedule='@hourly',  # Runs hourly
         catchup=False) as dag:

    # Define a Python task
    task1 = PythonOperator(
        task_id='run_task2',
        op_kwargs={'S3_BUCKET_NAME': 'university-hipolabs-usa',
                  'url': 'http://universities.hipolabs.com/search?country=United+States'},
        python_callable=upload_to_target.consume
    )
