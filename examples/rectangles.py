import teacup

"""
Pretty much the bare minimum you need to do anything using this library.
Opens a window and draws a few different colored rectangles.
"""

teacup.init() # init

# create the window
win = teacup.Window(
    "Rectangles", # title
    (400, 400), # size (x, y)
    { # uses CSS styling
        "background-color": (30, 30, 30, 255) # rgba
    }
)

# create the rectangles 
blue_rect = teacup.Rectangle(
    50, # x (upper left corner)
    50, # y 
    150, # width
    100, # height
    { # `background-color` is the main color for shapes
        "background-color": (50, 120, 255, 255)
    }
)

# same thing just different colors & positions
red_rect = teacup.Rectangle(100, 100, 150, 100, {"background-color": (255, 60, 60, 255)})
yellow_rect = teacup.Rectangle(150, 150, 150, 100, {"background-color": (255, 210, 60, 255)})

# attach the rectangles to the window
win.attach(blue_rect)
win.attach(red_rect)
win.attach(yellow_rect)

# main loop
while teacup.RUNNING(): # running keeps track of when windows are opened/closed for you
    teacup.display() # shortcut to render all of the currently open windows

teacup.done() # safely exit
