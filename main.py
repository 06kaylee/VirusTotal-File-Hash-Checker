import vt
import csv
import time
from datetime import datetime, timedelta
import config
import os
import pandas as pd
import numpy as np

client = vt.Client(config.api_key)



hash_file_path = config.hashes_from_splunk
hash_file_path2 = 'test.csv'


def read_in():
    hash_data = pd.read_csv(hash_file_path2)
    return hash_data


#check if new hash already exists in results3.csv
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
    
def first_write(hash_data):
    with open('results3.csv', mode = 'a', newline='') as results_file:
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
    return results.to_csv("results3.csv", index = False)

def write(hash_data):
    file_exists = os.path.isfile('results3.csv')
    if not file_exists:
        print("File is empty")
        first_write(hash_data)
    else:
        file_empty = os.stat('results3.csv').st_size == 0
        if file_empty:
            print("File is empty")
            first_write(hash_data)
        else:
            print("File is not empty")
            results = pd.read_csv('results3.csv')
            append(results, hash_data)


    # else:
    #     print("File is not empty")
    #     results = pd.read_csv('results3.csv')

# def write(hash_data):
#     with open('results3.csv', mode = 'a', newline='') as results_file:
#         file_empty = os.stat('results3.csv').st_size == 0
#         if file_empty:
#             writer = csv.writer(results_file, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#             print("File is empty")
#             fieldnames = ['Image', 'Hash', 'Result', 'Last Accessed']
#             writer.writerow(fieldnames)
#             for index, row in hash_data.iterrows():
#                 cur_image = row['Image']
#                 cur_hash = row['Hash']
#                 score, last_accessed = get_info(cur_hash)[0], get_info(cur_hash)[1]
#                 writer.writerow([cur_image, cur_hash, score, last_accessed])
#                 time.sleep(15)
#             return results_file
#         else:
#             print("File is not empty")
#             results = pd.read_csv('results3.csv')
#             for index, row in hash_data.iterrows():
#                 new_image = row['Image']
#                 new_hash = row['Hash']
#                 print(f'New image: {new_image} \t\t\t New hash: {new_hash}')
#                 if not hash_exists(results, new_hash):
#                     print("hash does not exist")
#                     score, last_accessed = get_info(new_hash)[0], get_info(new_hash)[1]
#                     results.loc[len(results)] = [new_image, new_hash, score, last_accessed]
#                     time.sleep(15)
#                 elif hash_exists(results, new_hash) and week_passed(results, new_hash):
#                     print("updating stuff")
#                     score, last_accessed = get_info(new_hash)[0], get_info(new_hash)[1]
#                     results.loc[results.Hash == new_hash, 'Last Accessed'] = last_accessed
#                     results.loc[results.Hash == new_hash, 'Result'] = score
#                     time.sleep(15)
#                 else:
#                     print("Nothing to be done")
#             return results.to_csv("results3.csv", index = False)
                

hash_data = read_in()
write(hash_data)


client.close()