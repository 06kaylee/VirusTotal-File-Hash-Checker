import vt
import csv
import time
from datetime import datetime
import config

client = vt.Client(config.api_key)

images = []
hashes = []

hash_file_path = config.hashes_from_splunk


def get_score(hash):
    try:
        file = client.get_object(f"/files/{hash}")
        return file.last_analysis_stats
    except Exception:
        return 'Unable to generate report on file'

def get_time():
    cur_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return cur_date

#open hash file splunk outputs  
with open(hash_file_path, mode = 'r') as hash_file:
    reader = csv.reader(hash_file, delimiter = ',')
    #skip header line
    hash_file.readline()
    for row in reader:
        images.append(row[0])
        hashes.append(row[1])
    with open('results.csv', mode = 'a', newline='') as results_file:
        fieldnames = ['Image', 'Hash', 'Result', 'Last Accessed']
        writer = csv.writer(results_file, delimiter = ',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(fieldnames)
        for index, image in enumerate(images):
            score = get_score(hashes[index])
            last_accessed = get_time()
            writer.writerow([image, hashes[index], score, last_accessed])
            #virustotal api only allows 4 requests/min
            time.sleep(15)




client.close()