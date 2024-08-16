import datetime
import os
import random
import requests
import string
from dotenv import load_dotenv

# https://stackoverflow.com/a/2257449
def rand_string(N):
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=N))

load_dotenv(); api_key = os.getenv('API_KEY')
start_date = datetime.datetime(2015, 8, 31)
end_date = datetime.today()

while start_date < end_date:
    fmt_date = start_date.strftime('%Y-%m-%d')
    url = f'https://api.nasa.gov/EPIC/api/natural/date/{'-'.join(fmt_date)}?api_key={api_key}'

    # ensure r contains a valid 200 response before continuing
    r = requests.get(url, headers={'User-agent': rand_string(8)})
    i = 0
    while r.status_code != 200 and i < 10:
        r = requests.get(url, headers={'User-agent': rand_string(8)})
        i += 1
    if i == 10:
        start_date += datetime.timedelta(days=1)
        continue

    response = list(reversed(r.json()));
    for row in response:
        refmt_date = '/'.join(fmt_date.split('-'))
        filename = row['image']
        image_url = f'https://api.nasa.gov/EPIC/archive/natural/{refmt_date}/png/{filename}.png?api_key={api_key}'

        s = filename[8:] # strip off 'epic_1b_' from start of string
        fmt_datetime = '-'.join([s[:4], s[4:6], s[6:8]]) + '_' + ':'.join([s[8:10], s[10:12], s[12:14]])
        file_to_save = f'orig/{fmt_datetime}.png'

        # save image_url as file_to_save
        open(file_to_save, 'wb').write(requests.get(image_url).content)

        # make copy in frames/ & edit with Pillow (add fmt_datetime to bottom centre of image)
        text = fmt_datetime.replace('_', ' ')
        # code...

    start_date += datetime.timedelta(days=1)

# lace images in frames/ into the final gif & video
# code...
