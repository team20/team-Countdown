
#!/usr/bin/env python3

import time
from datetime import datetime, timezone

from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
from pathlib import Path


# ==========================================
# CLIMATE CLOCK CONFIGURATION
# ==========================================

# CHANGE THIS TO YOUR ACTUAL COUNTDOWN DATE
TARGET_DATE = datetime(2027, 3, 11, tzinfo=timezone.utc)

# Display settings
ROWS = 32
COLS = 64
CHAIN_LENGTH = 2

HARDWARE_MAPPING = "adafruit-hat"
GPIO_SLOWDOWN = 2

# Display colors
GREEN = graphics.Color(0, 255, 0)
WHITE = graphics.Color(255, 255, 255)

# Text positioning
TEXT_X = 5
TOP_Y = 13
BOTTOM_Y = 28


# ==========================================
# DISPLAY INITIALIZATION
# ==========================================

def main():

    options = RGBMatrixOptions()

    options.rows = ROWS
    options.cols = COLS
    options.chain_length = CHAIN_LENGTH
    options.parallel = 1

    options.hardware_mapping = HARDWARE_MAPPING
    options.gpio_slowdown = GPIO_SLOWDOWN

    options.drop_privileges = False

    matrix = RGBMatrix(options=options)
    canvas = matrix.CreateFrameCanvas()

    # Load font from the same directory as this script
    font = graphics.Font()

    font_path = Path(__file__).parent / "6x13.bdf"
    font.LoadFont(str(font_path))

    try:

        while True:

            now = datetime.now(timezone.utc)
            remaining = (TARGET_DATE - now).total_seconds()

            canvas.Clear()

            if remaining <= 0:

                top_text = "00 days"
                bottom_text = "00:00:00.000"

            else:

                days = int(remaining // 86400)
                hours = int((remaining % 86400) // 3600)
                minutes = int((remaining % 3600) // 60)
                seconds = int(remaining % 60)
                milliseconds = int((remaining % 1) * 1000)

                top_text = f"{days:02} days"

                bottom_text = (
                    f"{hours:02}:"
                    f"{minutes:02}:"
                    f"{seconds:02}."
                    f"{milliseconds:03}"
                )

            graphics.DrawText(
                canvas, font,
                TEXT_X, TOP_Y,
                GREEN, top_text
            )

            graphics.DrawText(
                canvas, font,
                TEXT_X, BOTTOM_Y,
                WHITE, bottom_text
            )

            canvas = matrix.SwapOnVSync(canvas)

            time.sleep(0.01)

    except KeyboardInterrupt:

        print("Climate Clock stopped.")

    finally:

        matrix.Clear()


if __name__ == "__main__":
    main()
