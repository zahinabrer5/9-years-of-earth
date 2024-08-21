import datetime
import os
import random
import requests
import string
import sys
import time
from datetime import datetime as dt
from dotenv import load_dotenv
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw

# https://stackoverflow.com/a/2257449
def rand_string(N):
    return ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase + string.digits, k=N))

def process_img(img_src, img_dest, title, fontsize, padding):
    img = Image.open(img_src, 'r')
    draw = ImageDraw.Draw(img)
    w, h = img.size
    font = ImageFont.truetype("/usr/share/fonts/TTF/FiraCode-Regular.ttf", fontsize)
    text_w, text_h = draw.textlength(title, font), fontsize
    draw.text(((w - text_w) // 2, h - text_h - padding), title, (255,255,255), font=font)
    img.save(img_dest)
    return img_src

load_dotenv(); api_key = os.getenv('API_KEY')
start_date = datetime.datetime(2015, 8, 31)
# start_date = datetime.datetime(2016, 6, 27)
end_date = dt.today()

while start_date < end_date:
    fmt_date = start_date.strftime('%Y-%m-%d')
    url = f'https://api.nasa.gov/EPIC/api/natural/date/{'-'.join(fmt_date)}?api_key={api_key}'

    # ensure r contains a valid 200 response before continuing
    r = requests.get(url, headers={'User-agent': rand_string(16)})
    i = 0
    while r.status_code != 200 and i < 10:
        r = requests.get(url, headers={'User-agent': rand_string(32)})
        i += 1
    if i == 10:
        start_date += datetime.timedelta(days=1)
        continue

    response = list(reversed(r.json()));
    for row in response:
        refmt_date = '/'.join(fmt_date.split('-'))
        filename = row['image']
        actual_date = row['date'].replace(' ', '_')
        image_url = f'https://api.nasa.gov/EPIC/archive/natural/{refmt_date}/png/{filename}.png?api_key={api_key}'

        s = filename[8:] # strip off 'epic_1b_' from start of string
        save_path = os.path.join(sys.path[0]+'/orig/', actual_date+'.png')

        # save image_url to save_path
        print('Saving to '+save_path)
        open(save_path, 'wb').write(requests.get(image_url).content)

        # make copy in frames/ & edit with Pillow (add actual_date to bottom centre of image)
        text = actual_date.replace('_', ' ')
        dest_path = os.path.join(sys.path[0]+'/frames/', actual_date+'.png')
        print('Saving to '+dest_path)
        process_img(save_path, dest_path, text, 100, 75)

    start_date += datetime.timedelta(days=1)
    time.sleep(1)

# lace images in frames/ into the final gif & video
# https://stackoverflow.com/a/37478183
filename = '9-years-of-earth'
secondary = filename+'-orig'

print('Making mp4 from frames/')
os.system(f"ffmpeg -framerate 30 -pattern_type glob -i 'frames/*.png' \
    -c:v libx264 -pix_fmt yuv420p {filename}.mp4")

print('Making mp4 from orig/')
os.system(f"ffmpeg -framerate 30 -pattern_type glob -i 'orig/*.png' \
    -c:v libx264 -pix_fmt yuv420p {secondary}.mp4")
