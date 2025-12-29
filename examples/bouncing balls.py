import teacup
import random

"""
Bounces 20 balls off of the window's borders. Library stress test.
"""

teacup.init() # init teacup

# config
ball_radius = 10
total_balls = 20
gravity = 1
fps = 60

# create the window
screen_width, screen_height = 500, 500
my_win = teacup.Window(
    "Bouncing Balls",
    (screen_width, screen_height),
    {
        "background-color": (30, 30, 30, 255)
    }
)

balls = [ # list of all balls
    teacup.Ellipse(
        screen_width // 2 - ball_radius, # spawn in the middle, overriden later
        screen_height // 2 - ball_radius,
        ball_radius * 2, # width
        ball_radius * 2, # height
    ) for _ in range(total_balls)
]

# initilize all of the balls
for ball in balls:
    # random velocity
    ball.yvel = random.randint(-5, 5) # you can assign variables to teacup shapes
    ball.xvel = random.randint(-5, 5)

    # random position
    ball.x = random.randint(0, screen_width - ball.width) 
    ball.y = random.randint(0, screen_height - ball.height)

    # random color
    ball.style["background-color"] = (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        255
    )

    # attach the balls to the window
    my_win.attach(ball) 

# main loop
while teacup.RUNNING():
    for ball in balls: # loop through all balls
        # apply velocities
        ball.yvel += gravity

        # step ball forward
        ball.x += ball.xvel
        ball.y += ball.yvel

        # collide w/ floor & ceiling
        if ball.y + ball.height >= screen_height:
            ball.y = screen_height - ball.height
            ball.yvel *= -1 # bounce
            ball.yvel -= 1 # fix weird velocity bug
        elif ball.y < 0:
            ball.y = 0
            ball.yvel += 1 # fix weird velocity bug
            ball.yvel *= -1 # bounce

        # collide w/ left & right walls
        if ball.x < 0:
            ball.x = 0
            ball.xvel *= -1 # bounce
        elif ball.x + ball.width > screen_width:
            ball.x = screen_width - ball.width
            ball.xvel *= -1 # bounce

    teacup.display(fps) # does all of the ball drawing for you
    
teacup.done() # exit teacup
