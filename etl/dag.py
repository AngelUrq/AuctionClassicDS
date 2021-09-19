import sys
sys.path.append('/opt/airflow/dags/AuctionClassicDS/etl')

from datetime import datetime
from datetime import timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

from load_data import get_auction_data
from load_data import get_item_data

default_args = {
  'owner': 'airflow',
  'depends_on_past': False,
  'start_date': datetime(2021, 9, 18, 20, 0),
  'email_on_failure': True,
  'email_on_retry': False,
  'retries': 3,
  'retry_delay': timedelta(minutes=10)
}

dag = DAG(
  'auction_classic_dag',
  default_args=default_args,
  description='DAG to get auction data',
  schedule_interval=timedelta(hours=1)
)

auction_task = PythonOperator(
  task_id='auction_etl',
  python_callable=get_auction_data,
  dag=dag
)

item_task = PythonOperator(
  task_id='item_etl',
  python_callable=get_item_data,
  dag=dag
)

auction_task >> item_task