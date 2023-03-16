import requests
from zipfile import ZipFile
from io import BytesIO
import pandas as pd
from datetime import timedelta
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


TOP_1M_DOMAINS = 'http://s3.amazonaws.com/alexa-static/top-1m.csv.zip'
TOP_1M_DOMAINS_FILE = 'top-1m.csv'


def get_data():
    top_doms = requests.get(TOP_1M_DOMAINS, stream = True)
    zipfile = ZipFile(BytesIO(top_doms.content))
    top_data = zipfile.read(TOP_1M_DOMAINS_FILE).decode('utf-8')

    with open(TOP_1M_DOMAINS_FILE, 'w') as f:
        f.write(top_data)


def get_stat():
    top_data_df = pd.read_csv(TOP_1M_DOMAINS_FILE,  names = ['rank', 'domain'])
    top_data_10 = top_data_df[top_data_df['domain'].str.endswith('.ru') ]
    top_data_10 = top_data_10.head(10)
    with open('top_data_10.csv', 'w') as f:
        f.write(top_data_10.to_csv(index=  False, header = False))

def print_data():
    with open('top_data_10.csv', 'r') as f:
        all_data = f.read()
    print('Top domain in .RU')
    print(all_data)

default_args = {
    'owner': 'a.batalov',
    'depends_on_past': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'start_date': datetime(2021, 10, 7),
    'schedule_interval': '0 12 * * *'
}
dag = DAG('top_10_ru_new', default_args=default_args)


t1 = PythonOperator(task_id = 'get_data',
                    python_callable=get_data, 
                    dag = dag) 
t2 = PythonOperator(task_id = 'get_tat',
                    python_callable=get_stat,
                    dag = dag)
t3 = PythonOperator(task_id = 'print_data',
                    python_callable= print_data,
                    dag = dag)

t1 >> t2 >> t3

get_data()
get_stat()
print_data()