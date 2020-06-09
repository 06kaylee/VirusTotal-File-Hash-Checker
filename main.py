import vt
import csv
import time
from datetime import datetime, timedelta
import config
import os
import pandas as pd
import numpy as np
import sys

client = vt.Client(config.api_key)



def read_in(hash_file_path):
    hash_data = pd.read_csv(hash_file_path)
    return hash_data


def hash_exists(results, new_hash):
    if new_hash in results.values:
        return True
    else:
        return False


def get_score(hash):
    try:
        file = client.get_object(f"/files/{hash}")
        return file.last_analysis_stats
    except Exception:
        return 'Unable to generate report on file'


def get_time():
    cur_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    return cur_date   


def get_info(hash):
    score = get_score(hash)
    last_accessed = get_time()
    return [score, last_accessed]


def week_passed(results, hash):
    week = timedelta(days = 7)
    date = results.loc[results['Hash'] == hash, 'Last Accessed'].iloc[0]
    str_to_datetime = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
    elapsed_time = datetime.now() - str_to_datetime
    return elapsed_time > week


def first_write(hash_data, destination_path):
    with open(destination_path, mode = 'a', newline='') as results_file:
        writer = csv.writer(results_file, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        fieldnames = ['Image', 'Hash', 'Result', 'Last Accessed']
        print("Writing headers")
        writer.writerow(fieldnames)
        for index, row in hash_data.iterrows():
            cur_image = row['Image']
            cur_hash = row['Hash']
            print("Getting score")
            score, last_accessed = get_info(cur_hash)[0], get_info(cur_hash)[1]
            print("Adding result to file")
            writer.writerow([cur_image, cur_hash, score, last_accessed])
            time.sleep(15)
        return results_file


def append(results, hash_data):
    for index, row in hash_data.iterrows():
        new_image = row['Image']
        new_hash = row['Hash']
        if not hash_exists(results, new_hash):
            print("Hash does not exist")
            print("Getting score")
            score, last_accessed = get_info(new_hash)[0], get_info(new_hash)[1]
            print("Adding result to dataframe")
            results.loc[len(results)] = [new_image, new_hash, score, last_accessed]
            time.sleep(15)
        elif hash_exists(results, new_hash) and week_passed(results, new_hash):
            print("Updating hash result")
            print("Getting score")
            score, last_accessed = get_info(new_hash)[0], get_info(new_hash)[1]
            print("Modifying result and last access")
            results.loc[results.Hash == new_hash, 'Last Accessed'] = last_accessed
            results.loc[results.Hash == new_hash, 'Result'] = score
            time.sleep(15)
        else:
            print("Nothing to be done")
    return results.to_csv(destination_path, index = False)


def write(hash_data, destination_path):
    file_exists = os.path.isfile(destination_path)
    if not file_exists:
        print("File is empty")
        first_write(hash_data, destination_path)
    else:
        file_empty = os.stat(destination_path).st_size == 0
        if file_empty:
            print("File is empty")
            first_write(hash_data, destination_path)
        else:
            print("File is not empty")
            results = pd.read_csv(destination_path)
            append(results, hash_data, destination_path)


if len(sys.argv) == 1:
    hash_file_path = input("Enter the input filepath name (example: hashes.csv): ")
    destination_path = input("Enter the destination path (example: output.csv): ")
elif len(sys.argv) == 2:
    hash_file_path = sys.argv[1]
    destination_path = input("Enter the destination path (example: output.csv): ")
else:
    hash_file_path = sys.argv[1]
    destination_path = sys.argv[2]

hash_data = read_in(hash_file_path)
write(hash_data, destination_path)


client.close()