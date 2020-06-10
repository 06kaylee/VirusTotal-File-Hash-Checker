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


def first_write(hash_data, destination_path):
    with open(destination_path, mode = 'a', newline='') as results_file:
        writer = csv.writer(results_file, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        fieldnames = ['Hash', 'Undetected', 'Suspicious', 'Malicious', 'Name', 'Description', 'Last Accessed']
        print("Writing headers")
        writer.writerow(fieldnames)
        for i in hash_data.index:
            cur_hash = hash_data.loc[i].values[0]
            print(f"Getting info on: {cur_hash}")
            undetected, suspicious, malicious, name, description, last_accessed = get_info(cur_hash)[0], get_info(cur_hash)[1], get_info(cur_hash)[2], get_info(cur_hash)[3], get_info(cur_hash)[4], get_info(cur_hash)[5]
            print("Adding result to file")
            writer.writerow([cur_hash, undetected, suspicious, malicious, name, description, last_accessed])
            time.sleep(15)
        return results_file


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
    hash_file_path = input("Enter the input path (example: hashes.csv): ")
    destination_path = input("Enter the destination path (example: output.csv): ")
elif len(sys.argv) == 2:
    hash_file_path = sys.argv[1]
    destination_path = input("Enter the destination path (example: output.csv): ")
else:
    hash_file_path = sys.argv[1]
    destination_path = sys.argv[2]

hash_data = read_in(hash_file_path)
write(hash_data, destination_path)

append_to_input_file = input("Would you like to check more hashes and append them to the destination path? Y/N: ")
if(append_to_input_file.lower() == 'y' or append_to_input_file.lower() == 'yes'):
    hash_file_path = input("Enter the input path (example: hashes.csv): ")
    hash_data = read_in(hash_file_path)
    write(hash_data, destination_path)
else:
    print("Finished")

client.close()





