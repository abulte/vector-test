from datetime import date, timedelta
import logging
import os
import time

import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import requests

logging.basicConfig(level="DEBUG")

CATALOG_RESOURCE_IDS = {
    "resources": "4babf5f2-6a9c-45b5-9144-ca5eae6a7a6d",
    "datasets": "f868cca6-8da1-4369-a78d-47463f19a9a3",
    "reuses": "970aafa0-3778-4d8b-b9d1-de937525e379",
    "organizations": "b7bbfedc-2448-4135-a6c7-104548d396e7"
}


def download_file(url: str, target_filepath: str) -> str:
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(target_filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return target_filepath


def get_minio_url(netloc: str, bucket: str, key: str) -> str:
    '''Returns location of given resource in minio once it is saved'''
    return netloc + "/" + bucket + "/" + key


def get_s3_client(url: str, minio_user: str, minio_pwd: str) -> boto3.client:
    return boto3.client(
        "s3",
        endpoint_url=url,
        aws_access_key_id=minio_user,
        aws_secret_access_key=minio_pwd,
        config=Config(signature_version="s3v4"),
    )


def download_from_minio(netloc: str, bucket: str, key: str, filepath: str, minio_user: str, minio_pwd: str) -> None:
    logging.info("Downloading from minio")
    s3 = get_s3_client(netloc, minio_user, minio_pwd)
    try:
        s3.download_file(bucket, key, filepath)
        logging.info(
            f"Resource downloaded from minio at {get_minio_url(netloc, bucket, key)}"
        )
    except ClientError as e:
        logging.error(e)


while True:
    yesterday = date.today() - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y%m%d')
    log_filename = f"haproxy.log.{yesterday_str}"
    logs_folder = "logs"
    log_filepath = os.path.join(logs_folder, log_filename)
    os.makedirs(logs_folder, exist_ok=True)

    logging.debug(f"Checking if {log_filepath} exists")
    if not os.path.exists(log_filepath):
        logging.info("About to download")
        for catalog, catalog_id in CATALOG_RESOURCE_IDS.items():
            logging.info(f"Downloading {catalog} catalog")
            download_file(f"https://www.data.gouv.fr/fr/datasets/r/{catalog_id}", f"tables/{catalog}.csv")

        logging.info(f"Downloading to {log_filepath}...")
        download_from_minio(
            "https://object.files.data.gouv.fr",
            bucket="dataeng",
            key=f"prod-logs/{log_filename}",
            filepath=log_filepath,
            minio_user=os.environ["MINIO_USER"],
            minio_pwd=os.environ["MINIO_PASSWORD"],
        )

        # Remove previous day logs
        two_days_ago = (yesterday - timedelta(days=1)).strftime('%Y%m%d')
        previous_log_filename = f"haproxy.log.{two_days_ago}"
        previous_log_path = os.path.join(logs_folder, previous_log_filename)
        if os.path.exists(previous_log_path):
            os.remove(previous_log_path)

    time.sleep(60)