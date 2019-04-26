import pytz
import re
import requests
from datetime import datetime, timedelta
from io import BytesIO
from PIL import Image
import logging
import logging.config
import os
try:
    import configparser
except:
    from six.moves import configparser

# Project Zakolm
# https://github.com/zakolm/screen

# Fetch Himawari-8 full disks at a given zoom level and set as desktop.
# Valid zoom levels seem to be powers of 2, 1..16, and 20.
#
# To do:
# - Better errors (e.g., catch the "No Image" image).
# - Librarify.


def main():
    # Tile size for this dataset:
    width = 550
    height = 550
    scale = 8

    # Set time
    tz = pytz.timezone('Portugal')
    time = datetime.now(tz) - timedelta(minutes=40)

    # Set image path
    out = '/Users/marina/Desktop/Analysis_of_algorithms/screen_mac/screen.png'

    # http://himawari8-dl.nict.go.jp/himawari8/img/D531106/
    base = 'http://himawari8.nict.go.jp/img/D531106/%sd/550' % (scale)
    print(base)

    tiles = [[None] * scale] * scale

    path = "%s/%s/%02d/%02d/%02d%02d00" % (base, time.year, time.month, time.day, time.hour - 1, 00)
    try:
        fetch_and_set(path, width, height, scale, out)
    except requests.exceptions.ConnectionError:
        logging.error('Ошибка requests')
        try:
            fetch_and_set(path, width, height, scale, out)
        except requests.exceptions.ConnectionError:
            logging.error('Ошибка requests')


def pathfor(path, x, y):
    return path+"_%s_%s.png" % (x, y)


def fetch_and_set(path, width, height, scale, out):
    sess = requests.Session()  # so requests will reuse the connection
    png = Image.new('RGB', (width * scale, height * scale))
    logging.info('Начинаем собирать картинки')
    for x in range(scale):
        for y in range(scale):
            path_ = pathfor(path, x, y)
            logging.debug('Берем {} картинку из {}'.format((x+1)*y, scale*scale))
            tiledata = sess.get(path_).content
            tile = Image.open(BytesIO(tiledata))
            png.paste(tile, (width*x, height*y, width*(x+1), height*(y+1)))

    png.save(out, 'PNG')

    os.system("osascript -e 'tell application \"Finder\" to set desktop picture to POSIX file \"" + out + "\"'")
    os.system("killall Dock")
    sess.close()


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('logging.conf')
    logfile_path, logfile_name = re.findall('[A-z]+/[A-z]+.[A-z]+', config.get('handler_file', 'args'))[0].split('/')
    if not logfile_path in os.listdir('./'):
        os.mkdir(logfile_path)
    logging.config.fileConfig('logging.conf')
    logging.info('Начало программы')
    try:
        main()
    finally:
        logging.info('Конец программы')

