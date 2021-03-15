import sys
import time
import os
from alive_progress import alive_bar,show_bars, show_spinners, showtime

os.system('cls' if os.name == 'nt' else 'clear')

def compute():
    for i in range(100):
        time.sleep(.01)  # process items
        if i == 99:
            time.sleep(3)
        yield  # insert this and you're done!
with alive_bar(100) as bar:
    for i in compute():
        bar()
# showtime()