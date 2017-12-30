import os
import requests
from io import BytesIO
from subprocess import run
from zipfile import ZipFile
from lxml import etree

def windowsBuild():
    pyinstaller = 'pyinstaller'
    if 'PYINSTALLER_PATH' in os.environ:
        pyinstaller = os.environ['PYINSTALLER_PATH']

    ffmpegPageReq = requests.get('http://ffmpeg.zeranoe.com/builds/')
    html = etree.HTML(ffmpegPageReq.text)
    ffmpegVersion = html.xpath('//label[contains(@title, "Nightly")]/input')[0].attrib['value']
    ffmpegZipReq = requests.get('http://ffmpeg.zeranoe.com/builds/win64/static/ffmpeg-%s-win64-static.zip' % ffmpegVersion)
    ffmpegPath = 'ffmpeg-%s-win64-static/bin/ffmpeg.exe' % ffmpegVersion
    ZipFile(BytesIO(ffmpegZipReq.content)).extract(ffmpegPath)
    os.rename(ffmpegPath, 'ffmpeg.exe')
    run('%s -F -w --add-binary "ffmpeg.exe;ffmpeg.exe" music-dl.py' % pyinstaller, shell = True)

if os.name == 'nt':
    windowsBuild()
