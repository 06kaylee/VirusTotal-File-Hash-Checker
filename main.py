import vt
import csv
import time
from datetime import datetime, timedelta
import config
import os
import pandas as pd


client = vt.Client(config.api_key)

images = []
hashes = []

hash_file_path = config.hashes_from_splunk




#col_names = ['Image', 'Hash']





def get_score(hash):
    try:
        file = client.get_object(f"/files/{hash}")
        return file.last_analysis_stats
    except Exception:
        return 'Unable to generate report on file'

def get_time():
    # cur_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cur_date = datetime.now()
    return cur_date


def week_passed(last_accessed):
    add_week = timedelta(days = 7)
    str_to_datetime = datetime.strptime(last_accessed, '%Y-%m-%d %H:%M:%S.%f')
    print(str_to_datetime)
    print(str_to_datetime + add_week)
    return str_to_datetime > str_to_datetime + add_week
    #return str_to_datetime + add_week < str_to_datetime


def read_in():
    #open hash file splunk outputs  
    # with open(hash_file_path, mode = 'r') as hash_file:
    #     reader = csv.reader(hash_file, delimiter = ',')
    #     #skip header
    #     hash_file.readline()
    #     for row in reader:
    #         images.append(row[0])
    #         hashes.append(row[1])
    #hash_data = pd.read_csv(hash_file_path, names = col_names, header = 0)
    hash_data = pd.read_csv(hash_file_path)
    #print(hash_data.iloc[1])
    for index, row in hash_data.iterrows():
        images.append(row[0])
        hashes.append(row[1])
    return hash_data
    #print(hash_data.iloc[0, hash_data.columns.get_loc('Image')])



           
def get_info(hash):
    score = get_score(hash)
    last_accessed = get_time()
    return [score, last_accessed]

def write(hash_data):
    # with open('results2.csv', mode = 'a', newline='') as results_file:
    #     fieldnames = ['Image', 'Hash', 'Result', 'Last Accessed']
    #     writer = csv.writer(results_file, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #     file_empty = os.stat('results2.csv').st_size == 0
    #     if file_empty:
    #         writer.writerow(fieldnames)
    #     for index, image in enumerate(images):
    #         hash = hashes[index]
    #         print(f'Current hash: {hash}')
    #         if update_hash(hash):
    #             score, last_accessed = get_info(hash)[0], get_info(hash)[1]
    #             writer.writerow([image, hash, score, last_accessed])
    #             time.sleep(15)
    #         else:
    #             print("That hash has already been checked")
    # if file does not exist write header 
    col_names = ['Image', 'Hash', 'Result', 'Last Accessed']
    if not os.path.isfile('results3.csv'):
       hash_data.to_csv('results3.csv', index = False, header = col_names)
    else: # else it exists so append without writing the header
       hash_data.to_csv('results3.csv', mode='a', header=False)
    


def update_hash(hash):
    with open('results2.csv', mode = 'r') as results_file:
        reader = csv.reader(results_file, delimiter = ',')
        for row in reader:
            print(f'Hash: {hash} \t Value in file: {row[1]}')
            if row[1] == 'Hash':
                continue
            if hash == row[1] and not week_passed(row[3]):
                return False
            return True


# def start():
#     read_in()
#     write()

# start_time = time.time()
# start()
# end_time = time.time()
# print(f'Total time: {end_time - start_time}')



client.close()