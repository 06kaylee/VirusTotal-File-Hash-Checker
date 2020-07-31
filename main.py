import vt
import csv
import time
from datetime import datetime, timedelta
import config
import os
import pandas as pd
import numpy as np
import sys
import argparse

client = vt.Client(config.api_key)


def read_in(hash_file_path):
    hash_data = pd.read_csv(hash_file_path, header = None)
    return hash_data


def hash_exists(results, new_hash):
    if new_hash in results.values:
        return True
    else:
        return False


def get_undetected(file):
    try:
        return file.last_analysis_stats['undetected']
    except Exception:
        return 'n/a'


def get_suspicious(file):
    try:
        return file.last_analysis_stats['suspicious']
    except Exception:
        return 'n/a'


def get_malicious(file):
    try:
        return file.last_analysis_stats['malicious']
    except Exception:
        return 'n/a'


def get_name(file):
    try:
        return file.meaningful_name
    except Exception:
        return 'n/a'


def get_description(file):
    try:
        return file.type_description
    except Exception:
        return 'n/a'


def get_time():
    cur_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
    return cur_date   


def get_info(hash):
    try:
        file = client.get_object(f"/files/{hash}")
        undetected = get_undetected(file)
        suspicious = get_suspicious(file)
        malicious = get_malicious(file)
        name = get_name(file)
        description = get_description(file)
        last_accessed = get_time()
        return [undetected, suspicious, malicious, name, description, last_accessed]
    except vt.APIError:
        last_accessed = get_time()
        return ['n/a', 'n/a', 'n/a', 'n/a', 'n/a', last_accessed]
    except:
        return [0, 0, 0, 0, 0, 0]
    

def week_passed(results, hash):
    week = timedelta(days = 7)
    date = results.loc[results['Hash'] == hash, 'Last Accessed'].iloc[0]
    str_to_datetime = datetime.strptime(date, '%Y-%m-%d %H:%M:%S.%f')
    elapsed_time = datetime.now() - str_to_datetime
    return elapsed_time > week


def append(results, hash_data, destination_path):
    for i in hash_data.index:
        new_hash = hash_data.loc[i].values[0]
        print(f"Evaluating: {new_hash}")
        if not hash_exists(results, new_hash):
            print(f"{new_hash} does not exist in dataframe")
            print("Getting info")
            undetected, suspicious, malicious, name, description, last_accessed = get_info(new_hash)[0], get_info(new_hash)[1], get_info(new_hash)[2], get_info(new_hash)[3], get_info(new_hash)[4], get_info(new_hash)[5]
            print("Adding result to dataframe")
            results.loc[len(results)] = [new_hash, undetected, suspicious, malicious, name, description, last_accessed]
            time.sleep(15)
        elif hash_exists(results, new_hash) and week_passed(results, new_hash):
            print(f"{new_hash} is being updated")
            print("Getting score")
            undetected, suspicious, malicious, name, description, last_accessed = get_info(new_hash)[0], get_info(new_hash)[1], get_info(new_hash)[2], get_info(new_hash)[3], get_info(new_hash)[4], get_info(new_hash)[5]
            print("Modifying result and last access")
            results.loc[results.Hash == new_hash, ['Last Accessed', 'Undetected', 'Suspicious', 'Malicious']] = [last_accessed, undetected, suspicious, malicious]
            time.sleep(15)
        else:
            print("Nothing to be done")
    return results.to_csv(destination_path, index = False)


def first_write(hash_data, destination_path):
    file_exists = os.path.isfile(destination_path)
    columns = ['Hash', 'Undetected', 'Suspicious', 'Malicious', 'Name', 'Description', 'Last Accessed']
    results = pd.DataFrame(columns = columns)
    for i in hash_data.index:
        hash_result = []
        cur_hash = hash_data.loc[i].values[0]
        print(f"Getting info on: {cur_hash}")
        undetected, suspicious, malicious, name, description, last_accessed = get_info(cur_hash)[0], get_info(cur_hash)[1], get_info(cur_hash)[2], get_info(cur_hash)[3], get_info(cur_hash)[4], get_info(cur_hash)[5]
        print("Adding result to file")
        hash_result.extend([cur_hash, undetected, suspicious, malicious, name, description, last_accessed])
        results.loc[len(results) + 1] = hash_result
        time.sleep(15)
    results_file = results.to_csv(destination_path, index = False)
    return results_file


def write_options(hash_data, destination_path):
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


parser = argparse.ArgumentParser()
parser.add_argument("InputPath", help = "Enter the csv file path where the hashes to be checked are stored. Example: hashes.csv")
parser.add_argument("DestinationPath", help = "Enter the csv file path where you want the results to be stored. Example: output.csv")
args = parser.parse_args()
hash_file_path = args.InputPath
destination_path = args.DestinationPath

hash_data = read_in(hash_file_path)
start_time = time.time()
write_options(hash_data, destination_path)
end_time = time.time()
print(f'Total time: {end_time - start_time}')

client.close()





