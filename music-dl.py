from __future__ import unicode_literals
from appJar import gui
from youtube_dl import YoutubeDL
import sys
import os

app = gui()

# From: https://stackoverflow.com/questions/7674790/bundling-data-files-with-pyinstaller-onefile
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def writeOutput(msg):
    try:
        app.setTextArea("output", "%s\n" % msg)
    except:
        app.setTextArea("output", sys.exc_info())
        app.setTextArea("output", "\n")

class Logger(object):
    def debug(self, msg):
        app.queueFunction(writeOutput, msg)

    def warning(self, msg):
        app.queueFunction(writeOutput, msg)
            
    def error(self, msg):
        app.queueFunction(writeOutput, msg)

def dlProgress(progress):
    total = 0
    if progress['total_bytes'] != None:
        total = (progress['downloaded_bytes'] / progress['total_bytes']) * 100
    elif progress['total_bytes_estimate'] != None:
        total = (progress['downloaded_bytes'] / progress['total_bytes_estimate']) * 100

    app.queueFunction(app.setMeter, "progress", total)

    if progress['status'] == 'finished' or progress['status'] == 'error':
        app.enableButton("Download")
        app.enableEntry("URL")
        app.enableDirectoryEntry("destination")

def download(url, destination, logger):
    opts = {
        'format': 'm4a/bestaudio',
        'outtmpl': destination + '/%(title)s.%(ext)s',
        'logger': logger,
        'progress_hooks': [dlProgress],
        'postprocessors': [
            {
                'key': 'MetadataFromTitle',
                'titleformat': '%(artist)s - %(title)s'
            },
            {
                'key': 'FFmpegMetadata'
            }
        ],
        'ffmpeg_location': resource_path('ffmpeg.exe')
    }
    ydl = YoutubeDL(opts)
    ydl.add_default_info_extractors()
    try:
        ydl.download([url])
    except:
        app.enableButton("Download")
        app.enableEntry("URL")
        app.enableDirectoryEntry("destination")
        app.queueFunction(writeOutput, sys.exc_info())

def dlBtnPress(btn):
    app.disableButton("Download")
    app.disableEntry("URL")
    app.disableDirectoryEntry("destination")
    app.setMeter("progress", 0)
    app.clearTextArea("output")
    app.thread(download, app.getEntry("URL"), app.getEntry("destination"), Logger())

def checkEnableBtn(arg):
    if app.getEntry("URL") != None and app.getEntry("destination"):
        app.enableButton("Download")
        app.setMeter("progress", 0)
        app.clearTextArea("output")
    else:
        app.disableButton("Download")

app.addLabelEntry("URL")
app.setEntryChangeFunction("URL", checkEnableBtn)
app.addDirectoryEntry("destination")
app.setDirectoryEntryChangeFunction("destination", checkEnableBtn)
app.addButton("Download", dlBtnPress)
app.disableButton("Download")
app.addMeter("progress")
app.addScrolledTextArea("output")

app.go()
