import teacup
from colorsys import hsv_to_rgb

"""
Open 2 windows, one with text that is rainbow colored and another that's background is rainbow
colored. Teacup allows you to create & open multiple windows. 5 Fonts are packaged with Teacup,
if you want to use your own you must add it to teacup with `teacup.font.create_custom_font(...)`.
"""

teacup.init() # init teacup

# create windows
win1 = teacup.Window("Rainbow Window", (500, 500))
win2 = teacup.Window("Rainbow Text", (500, 500), {"background-color": (255, 255, 255, 255)})

# settings
fps = 60
dt = 0 # placeholder
hue = 0
speed = 90 # how fast the window's cycle colors

# create text objects
text1 = teacup.Text(
    100, # x
    100, # y
    "This is a rainbow window!", # text
    { # shorthand isn't supported as of teacup 0.1.0
        "font-family": "Inter", # `teacup.font.get_loaded_font_names()` to get more fonts
        "font-size": 24,
        "color": (255, 255, 255, 255), # text color (rgba)
    }
)

text2 = teacup.Text( # same thing
    100,
    100,
    "This is rainbow text!",
    {
        "font-family": "Inter",
        "font-size": 24,
        "color": (255, 255, 255, 255),
    }
)

# attach the text objects to their own windows
win1.attach(text1)
win2.attach(text2)

# main loop
while teacup.RUNNING():
    hue = (hue + dt * speed) % 360 # increment hue
    r, g, b = hsv_to_rgb(hue / 360, 1, 1) # convert from hsv

    # rainbow window
    win1.style["background-color"] = (
        int(r * 255),
        int(g * 255),
        int(b * 255),
        255 # alpha channel
    )

    # rainbow text
    text2.style["color"] = ( # modify the color attribute instead of `background-color` for text
        int(r * 255),
        int(g * 255),
        int(b * 255),
        255
    )

    dt = teacup.display(fps) # returns deltatime

teacup.done() # don't forget to close
