from teacup import Window
import time

# open a window and close it 10 seconds later
with Window() as my_win:
    time.sleep(10)
    my_win.kill()
