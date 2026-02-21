#!/usr/bin/env python3

import json
import os
import sys
import time
from datetime import datetime, timezone, timedelta

import config
import requests
from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics

# Added PIL to handle the Team 20 logo
from PIL import Image

EST = timezone(timedelta(hours=-5))


"""
TIME_COLOR = '#ffd919'
TIME_ALT_COLOR = '#c8890a'
BUDGET_COLOR = '#9900e6'
BUDGET_ALT_COLOR = '#671497'


# TODO: Pull these from the network
JSON = 'https://raw.githubusercontent.com/beautifultrouble/climate-clock-widget/master/src/clock.json'
SECONDS_PER_YEAR = 365.25 * 24 * 3600
START_DATE = datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
START_EMISSIONS_BUDGET = 4.2e11
START_EMISSIONS_YEARLY = 4.2e10


relpath = lambda filename: os.path.join(sys.path[0], filename)
hex2color = lambda x: graphics.Color(int(x[-6:-4], 16), int(x[-4:-2], 16), int(x[-2:], 16))


def time_and_budget():
    '''
    Return the time (in seconds) until the carbon budget is spent, and the
    remaining carbon budget (in tons).
    '''
    now = datetime.now(timezone.utc)
    emissions_per_second = START_EMISSIONS_YEARLY / SECONDS_PER_YEAR
    emissions_budget_spent = ((now - START_DATE).total_seconds() * emissions_per_second)
    emissions_budget = START_EMISSIONS_BUDGET - emissions_budget_spent
    time_remaining = emissions_budget / emissions_per_second
    
    return time_remaining, emissions_budget


def run(options):
    matrix = RGBMatrix(options=options)
    canvas = matrix.CreateFrameCanvas()

    font_file = ['5x8.bdf', '6x13B.bdf', '9x18B.bdf'][options.chain_length - 1]
    font = graphics.Font()
    font.LoadFont(relpath(font_file))

    t_color = hex2color(TIME_COLOR)
    ta_color = hex2color(TIME_ALT_COLOR)
    b_color = hex2color(BUDGET_COLOR)
    ba_color = hex2color(BUDGET_ALT_COLOR)

    while not time.sleep(.1):
        time_remaining, emissions_budget = time_and_budget()

        years, r = divmod(time_remaining, SECONDS_PER_YEAR)
        days, r = divmod(r, 24 * 3600)
        hours, r = divmod(r, 3600)
        minutes, seconds = divmod(r, 60)

        canvas.Clear()

        t_strings = [
            f"{years:1.0f}",
            f"{'YR' if years == 1 else 'YRS'}",
            f"{days:3.0f}",
            f"{'DAY' if days == 1 else 'DAYS'}",
            f"{hours:02.0f}:{minutes:02.0f}:{seconds:02.0f}",
        ]
        b_strings = [
            f"{int(emissions_budget):,}"[:12],
            f"{int(emissions_budget):,}"[12:],
            f"TONS",
        ]

        # Place text fragments according to number of screens
        t_colors = [t_color, ta_color, t_color, ta_color, t_color]
        b_colors = [b_color, b_color, ba_color]
        if options.chain_length == 3:
            t_pos = (2, 14), (16, 14), (47, 14), (78, 14), (118, 14)
            b_pos = (2, 28), (111, 28), (145, 28)
        elif options.chain_length == 2:
            t_pos = (2, 14), (10, 14), (31, 14), (51, 14), (78, 14)
            b_pos = (2, 28), (74, 28), (96, 28)
        elif options.chain_length == 1:
            t_pos = (3, 7), (9, 7), (26, 7), (42, 7), (3, 15), (42, 15)
            t_strings.append(f".{int(seconds%1*1000):03d}")
            t_colors.append(t_color) 
            b_pos = (3, 23), (3, 31), (22, 31)
            b_strings[2] = "TONS CO₂"

        for pos, strings, colors in ((t_pos, t_strings, t_colors), (b_pos, b_strings, b_colors)):
            for (x, y), s, c in zip(pos, strings, colors):
                graphics.DrawText(canvas, font, x, y, c, s)

        canvas = matrix.SwapOnVSync(canvas)


options = RGBMatrixOptions()
for key, value in vars(config).items():
    if not key.startswith('__'):
        setattr(options, key, value)

run(options)
"""

# NEW TEAM 20 CONSTANTS
TEAM_COLOR = graphics.Color(0, 255, 0) # Green from logo
TEXT_COLOR = graphics.Color(255, 255, 255) # White
TARGET_DATE = datetime(2026, 3, 11, 0, 0, 0, tzinfo=EST)

relpath = lambda filename: os.path.join(sys.path[0], filename)

def run(options):
    matrix = RGBMatrix(options=options)
    canvas = matrix.CreateFrameCanvas()
    
    # Load Font
    font = graphics.Font()
    font.LoadFont(relpath('6x13B.bdf'))

    # Load Logo
    try:
        logo = Image.open(relpath("Team20.png")).convert('RGB')
    except Exception as e:
        print(f"Could not load Team20.png: {e}")
        logo = None

    while True:
        now = datetime.now(timezone.utc)
        diff = TARGET_DATE - now
        total_seconds = diff.total_seconds()
        
        # 1. ALWAYS CLEAR FIRST
        canvas.Clear()

        if total_seconds < 0:
            countdown_top = "00 days"
            countdown_bot = "00:00:00.000"
        else:
            days = diff.days
            hours, rem = divmod(diff.seconds, 3600)
            minutes, seconds = divmod(rem, 60)
            # Correct countdown milliseconds
            msec = int((total_seconds % 1) * 1000)

            countdown_top = f"{days} days"
            countdown_bot = f"{hours:02}:{minutes:02}:{seconds:02}.{msec:03d}"

        # 2. DRAW LOGO
        if logo:
            # Note: Ensure logo is small enough for the panel
            canvas.SetImage(logo, 0, 0)

        # 3. DRAW TEXT
        # If your logo is 32 pixels wide, try x_offset = 33
        x_offset = 55 
        graphics.DrawText(canvas, font, x_offset, 13, TEAM_COLOR, countdown_top)
        graphics.DrawText(canvas, font, x_offset, 28, TEXT_COLOR, countdown_bot)

        # 4. SWAP TO DISPLAY
        canvas = matrix.SwapOnVSync(canvas)
        
        # Keep sleep low for smooth milliseconds
        time.sleep(0.01)

options = RGBMatrixOptions()

# Disable the internal "frame-throttling" to let it run as fast as possible
options.disable_hardware_pulsing = False 

# Try setting this lower if you still see flicker; 
# it forces the Pi to use a different hardware timer.
options.pwm_lsb_nanoseconds = 130 

# Reduce PWM bits if necessary to boost refresh rate (default is 11)
# Dropping to 7 or 8 makes the display MUCH smoother but slightly less color-accurate
options.pwm_bits = 7 

# Slow down the GPIO to prevent "ghost" pixels (0-4, try 2 or 3)
options.gpio_slowdown = 2 

# Grabs the setings for using an Adafruit Hat/Bonnet
options.hardware_mapping = 'adafruit-hat'

# Apply your other config settings
for key, value in vars(config).items():
    if not key.startswith('__'):
        setattr(options, key, value)

run(options)