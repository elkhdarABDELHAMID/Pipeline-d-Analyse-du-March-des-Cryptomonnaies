from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
import requests
import json
import subprocess
import happybase
import os
import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

default_args = {
    'owner': 'etudiant',
    'depends_on_past': False,
    'start_date': datetime(2025, 2, 24),
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

def fetch_coingecko_data(**context):
    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        'vs_currency': 'usd',
        'order': 'market_cap_desc',
        'per_page': '100',
        'page': '1',
        'sparkline': 'false'
    }
    response = requests.get(url, params=params)
    data = response.json()
    context['ti'].xcom_push(key='raw_data', value=data)

def store_raw_data_in_hdfs(**context):
    data = context['ti'].xcom_pull(key='raw_data')
    json_data = json.dumps(data)
    local_file = '/mnt/hadoop_data/coingecko_raw.json'
    with open(local_file, 'w') as f:
        f.write(json_data)
    execution_date = context['ds']
    year, month, day = execution_date.split('-')
    hdfs_dir = f"/user/etudiant/crypto/raw/YYYY={year}/MM={month}/DD={day}"
    hdfs_file_path = f"{hdfs_dir}/coingecko_raw.json"
    subprocess.run(["docker", "exec", "-i", "-u", "root", "namenode", "hdfs", "dfs", "-mkdir", "-p", hdfs_dir])
    subprocess.run(["docker", "exec", "-i", "-u", "root", "namenode", "hdfs", "dfs", "-put", "-f", local_file, hdfs_file_path])

def load_to_hbase(**context):
    execution_date = context['ds']
    year, month, day = execution_date.split('-')
    hdfs_dir = f"/user/etudiant/crypto/processed/YYYY={year}/MM={month}/DD={day}/"
    local_file = "/home/airflow/tmp/crypto_agg.csv"  # مسار جديد

    os.makedirs(os.path.dirname(local_file), exist_ok=True)

    if os.path.exists(local_file):
        try:
            os.remove(local_file)
            logger.info(f"Deleted existing local file: {local_file}")
        except PermissionError as e:
            logger.error(f"Failed to delete {local_file}: {e}")

    result = subprocess.run(
        ["docker", "exec", "-i", "-u", "root", "namenode", "hdfs", "dfs", "-get", "-f", hdfs_dir + "part-00000", "/tmp/crypto_agg.csv"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"Failed to get file from HDFS: {result.stderr}")
    logger.info(f"Downloaded to namenode: {result.stdout}")

    result = subprocess.run(
        ["docker", "cp", "namenode:/tmp/crypto_agg.csv", local_file],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise Exception(f"Failed to copy file from namenode: {result.stderr}")
    logger.info(f"Copied to {local_file}")

    connection = happybase.Connection('hbase', port=9090)
    try:
        tables = connection.tables()
        if b'crypto_prices' not in tables:
            connection.create_table('crypto_prices', {'stats': dict()})
        table = connection.table('crypto_prices')
        with table.batch() as b:
            with open(local_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        coin_id, min_p, max_p, avg_p, std_p, vol_sum, count = line.split(',')
                        row_key = f"{coin_id}_{execution_date}"
                        b.put(row_key, {
                            'stats:price_min': min_p,
                            'stats:price_max': max_p,
                            'stats:price_avg': avg_p,
                            'stats:price_std_dev': std_p,
                            'stats:volume_sum': vol_sum,
                            'stats:count': count
                        })
                    except ValueError as e:
                        logger.error(f"Error processing line: {line} - {e}")
    finally:
        connection.close()



"""
with DAG(
    'coingecko_ingestion_dag',
    default_args=default_args,
    schedule_interval='@daily'
) as dag:
"""


with DAG(
    'coingecko_ingestion_dag',
    default_args=default_args,
    schedule_interval='20 14 * * *'
) as dag:

    fetch_data = PythonOperator(
        task_id='fetch_data',
        python_callable=fetch_coingecko_data,
        provide_context=True
    )

    store_raw_data = PythonOperator(
        task_id='store_raw_data_in_hdfs',
        python_callable=store_raw_data_in_hdfs,
        provide_context=True
    )

    run_mapreduce_job = BashOperator(
        task_id='run_mapreduce_job',
        bash_command="""
        OUTPUT_DIR="/user/etudiant/crypto/processed/YYYY={{ execution_date.year }}/MM={{ execution_date.strftime('%m') }}/DD={{ execution_date.strftime('%d') }}"
        docker exec -i namenode bash -c "hdfs dfs -test -d $OUTPUT_DIR && hdfs dfs -rm -r $OUTPUT_DIR || echo 'Directory does not exist, proceeding...'"
        docker exec -i namenode \
        hadoop jar /opt/hadoop-3.2.1/share/hadoop/tools/lib/hadoop-streaming-3.2.1.jar \
        -input /user/etudiant/crypto/raw/YYYY={{ execution_date.year }}/MM={{ execution_date.strftime('%m') }}/DD={{ execution_date.strftime('%d') }}/coingecko_raw.json \
        -output $OUTPUT_DIR \
        -mapper "python3 /tmp/mapper.py" \
        -reducer "python3 /tmp/reducer.py" 2>/tmp/mapreduce.log
        docker exec -i namenode hdfs dfs -test -e $OUTPUT_DIR/part-00000 || (echo "MapReduce failed to produce output. Check /tmp/mapreduce.log for details" && exit 1)
        """,
        retries=3,
        retry_delay=timedelta(minutes=5)
    )

    load_to_hbase_task = PythonOperator(
        task_id='load_to_hbase',
        python_callable=load_to_hbase,
        provide_context=True
    )

    fetch_data >> store_raw_data >> run_mapreduce_job >> load_to_hbase_task