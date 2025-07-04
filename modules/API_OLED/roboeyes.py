# This Python script is a port and adaptation of the file FluxGarage_RoboEyes.h in the project
# "RoboEyes" by Dennis Hoelscher.
# Original project information:
# Copyright (C) 2024 Dennis Hoelscher
# www.fluxgarage.com
# www.youtube.com/@FluxGarage
#
# The original C++ project is licensed under the GNU General Public License v3.0.
# This Python adaptation is also licensed under the GNU General Public License v3.0.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


import random
import time

from PIL import Image, ImageDraw

# Usage of monochrome display colors
BGCOLOR = 0  # background and overlays
MAINCOLOR = 1  # drawings

# For mood type switch
DEFAULT = 0
TIRED = 1
ANGRY = 2
HAPPY = 3

# For turning things on or off
ON = 1
OFF = 0

# For switch "predefined positions"
N = 1  # north, top center
NE = 2  # north-east, top right
E = 3  # east, middle right
SE = 4  # south-east, bottom right
S = 5  # south, bottom center
SW = 6  # south-west, bottom left
W = 7  # west, middle left
NW = 8  # north-west, top left
# for middle center set "DEFAULT"


class RoboEyes:
    def __init__(self, screen_width=128, screen_height=64, frame_rate=50):
        # For general setup - screen size and max. frame rate
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.frame_interval = 1.0 / frame_rate  # in seconds
        self.fps_timer = 0  # for timing the frames per second

        # Pillow Image
        self.image = Image.new("1", (self.screen_width, self.screen_height), BGCOLOR)
        self.draw = ImageDraw.Draw(self.image)

        # For controlling mood types and expressions
        self.tired = False
        self.angry = False
        self.happy = False
        self.curious = (
            False  # if true, draw the outer eye larger when looking left or right
        )
        self.cyclops = False  # if true, draw only one eye
        self.eyeL_open = False  # left eye opened or closed?
        self.eyeR_open = False  # right eye opened or closed?

        # *********************************************************************************************
        #  Eyes Geometry
        # *********************************************************************************************

        # EYE LEFT - size and border radius
        self.eyeL_width_default = 36
        self.eyeL_height_default = 36
        self.eyeL_width_current = self.eyeL_width_default
        self.eyeL_height_current = (
            1  # start with closed eye, otherwise set to eyeL_height_default
        )
        self.eyeL_width_next = self.eyeL_width_default
        self.eyeL_height_next = self.eyeL_height_default
        self.eyeL_height_offset = 0
        # Border Radius
        self.eyeL_border_radius_default = 8
        self.eyeL_border_radius_current = self.eyeL_border_radius_default
        self.eyeL_border_radius_next = self.eyeL_border_radius_default

        # EYE RIGHT - size and border radius
        self.eyeR_width_default = self.eyeL_width_default
        self.eyeR_height_default = self.eyeL_height_default
        self.eyeR_width_current = self.eyeR_width_default
        self.eyeR_height_current = (
            1  # start with closed eye, otherwise set to eyeR_height_default
        )
        self.eyeR_width_next = self.eyeR_width_default
        self.eyeR_height_next = self.eyeR_height_default
        self.eyeR_height_offset = 0
        # Border Radius
        self.eyeR_border_radius_default = 8
        self.eyeR_border_radius_current = self.eyeR_border_radius_default
        self.eyeR_border_radius_next = self.eyeR_border_radius_default

        # Space between eyes - Moved up for correct initialization order
        self.spaceBetween_default = 10
        self.spaceBetween_current = self.spaceBetween_default
        self.spaceBetween_next = 10

        # EYE LEFT - Coordinates
        self.eyeL_x_default = (
            (self.screen_width)
            - (
                self.eyeL_width_default
                + self.spaceBetween_default
                + self.eyeR_width_default
            )
        ) // 2
        self.eyeL_y_default = (self.screen_height - self.eyeL_height_default) // 2
        self.eyeL_x = self.eyeL_x_default
        self.eyeL_y = self.eyeL_y_default
        self.eyeL_x_next = self.eyeL_x
        self.eyeL_y_next = self.eyeL_y

        # EYE RIGHT - Coordinates
        self.eyeR_x_default = (
            self.eyeL_x + self.eyeL_width_current + self.spaceBetween_default
        )
        self.eyeR_y_default = self.eyeL_y
        self.eyeR_x = self.eyeR_x_default
        self.eyeR_y = self.eyeR_y_default
        self.eyeR_x_next = self.eyeR_x
        self.eyeR_y_next = self.eyeR_y

        # BOTH EYES
        # Eyelid top size
        self.eyelids_height_max = (
            self.eyeL_height_default // 2
        )  # top eyelids max height
        self.eyelids_tired_height = 0
        self.eyelids_tired_height_next = self.eyelids_tired_height
        self.eyelids_angry_height = 0
        self.eyelids_angry_height_next = self.eyelids_angry_height
        # Bottom happy eyelids offset
        self.eyelids_happy_bottom_offset_max = (self.eyeL_height_default // 2) + 3
        self.eyelids_happy_bottom_offset = 0
        self.eyelids_happy_bottom_offset_next = 0

        # *********************************************************************************************
        #  Macro Animations
        # *********************************************************************************************

        # Animation - horizontal flicker/shiver
        self.h_flicker = False
        self.h_flicker_alternate = False
        self.h_flicker_amplitude = 2

        # Animation - vertical flicker/shiver
        self.v_flicker = False
        self.v_flicker_alternate = False
        self.v_flicker_amplitude = 10

        # Animation - auto blinking
        self.autoblinker = False  # activate auto blink animation
        self.blink_interval = 1  # basic interval between each blink in full seconds
        self.blink_interval_variation = 4  # interval variaton range in full seconds, random number inside of given range will be add to the basic blink_interval, set to 0 for no variation
        self.blinktimer = 0  # for organising eyeblink timing

        # Animation - idle mode: eyes looking in random directions
        self.idle = False
        self.idle_interval = (
            1  # basic interval between each eye repositioning in full seconds
        )
        self.idle_interval_variation = 3  # interval variaton range in full seconds, random number inside of given range will be add to the basic idle_interval, set to 0 for no variation
        self.idle_animation_timer = 0  # for organising eyeblink timing

        # Animation - eyes confused: eyes shaking left and right
        self.confused = False
        self.confused_animation_timer = 0
        self.confused_animation_duration = 0.5  # seconds
        self.confused_toggle = True

        # Animation - eyes laughing: eyes shaking up and down
        self.laugh = False
        self.laugh_animation_timer = 0
        self.laugh_animation_duration = 0.5  # seconds
        self.laugh_toggle = True

        self.begin(screen_width, screen_height, frame_rate)

    # *********************************************************************************************
    #  GENERAL METHODS
    # *********************************************************************************************
    def begin(self, width, height, frame_rate):
        self.screen_width = width
        self.screen_height = height
        self.draw.rectangle(
            [(0, 0), (self.screen_width, self.screen_height)], fill=BGCOLOR
        )  # clear image
        # self.image.save("debug_begin.png") # for debugging image state
        self.eyeL_height_current = 1  # start with closed eyes
        self.eyeR_height_current = 1  # start with closed eyes
        self.set_framerate(frame_rate)

    def update(self):
        # Limit drawing updates to defined max framerate
        current_time = time.monotonic()
        if current_time - self.fps_timer >= self.frame_interval:
            self.draw_eyes()
            self.fps_timer = current_time
            return self.image  # Return the image for external use
        return None

    # *********************************************************************************************
    #  SETTERS METHODS
    # *********************************************************************************************
    def set_framerate(self, fps):
        if fps > 0:
            self.frame_interval = 1.0 / fps
        else:
            self.frame_interval = 0.02  # Default to 50 FPS if fps is 0 or negative

    def set_width(self, left_eye, right_eye):
        self.eyeL_width_next = left_eye
        self.eyeR_width_next = right_eye
        self.eyeL_width_default = left_eye
        self.eyeR_width_default = right_eye

    def set_height(self, left_eye, right_eye):
        self.eyeL_height_next = left_eye
        self.eyeR_height_next = right_eye
        self.eyeL_height_default = left_eye
        self.eyeR_height_default = right_eye

    def set_borderradius(self, left_eye, right_eye):
        self.eyeL_border_radius_next = left_eye
        self.eyeR_border_radius_next = right_eye
        self.eyeL_border_radius_default = left_eye
        self.eyeR_border_radius_default = right_eye

    def set_spacebetween(self, space):
        self.spaceBetween_next = space
        self.spaceBetween_default = space

    def set_mood(self, mood):
        if mood == TIRED:
            self.tired = True
            self.angry = False
            self.happy = False
        elif mood == ANGRY:
            self.tired = False
            self.angry = True
            self.happy = False
        elif mood == HAPPY:
            self.tired = False
            self.angry = False
            self.happy = True
        else:  # DEFAULT
            self.tired = False
            self.angry = False
            self.happy = False

    def get_screen_constraint_X(self):
        return (
            self.screen_width
            - self.eyeL_width_current
            - self.spaceBetween_current
            - self.eyeR_width_current
        )

    def get_screen_constraint_Y(self):
        return self.screen_height - self.eyeL_height_default

    def set_position(self, position):
        constraint_x = self.get_screen_constraint_X()
        constraint_y = self.get_screen_constraint_Y()

        if position == N:
            self.eyeL_x_next = constraint_x // 2
            self.eyeL_y_next = 0
        elif position == NE:
            self.eyeL_x_next = constraint_x
            self.eyeL_y_next = 0
        elif position == E:
            self.eyeL_x_next = constraint_x
            self.eyeL_y_next = constraint_y // 2
        elif position == SE:
            self.eyeL_x_next = constraint_x
            self.eyeL_y_next = constraint_y
        elif position == S:
            self.eyeL_x_next = constraint_x // 2
            self.eyeL_y_next = constraint_y
        elif position == SW:
            self.eyeL_x_next = 0
            self.eyeL_y_next = constraint_y
        elif position == W:
            self.eyeL_x_next = 0
            self.eyeL_y_next = constraint_y // 2
        elif position == NW:
            self.eyeL_x_next = 0
            self.eyeL_y_next = 0
        else:  # DEFAULT
            self.eyeL_x_next = constraint_x // 2
            self.eyeL_y_next = constraint_y // 2

        # Right eye position is dependent on left eye in draw_eyes, so we only need to set left eye's target
        self.eyeR_x_next = (
            self.eyeL_x_next + self.eyeL_width_current + self.spaceBetween_current
        )
        self.eyeR_y_next = self.eyeL_y_next

    def set_autoblinker(self, active, interval=1, variation=4):
        self.autoblinker = active
        self.blink_interval = interval
        self.blink_interval_variation = variation

    def set_idle_mode(self, active, interval=1, variation=3):
        self.idle = active
        self.idle_interval = interval
        self.idle_interval_variation = variation

    def set_curiosity(self, curious_bit):
        self.curious = curious_bit

    def set_cyclops(self, cyclops_bit):
        self.cyclops = cyclops_bit

    def set_h_flicker(self, flicker_bit, amplitude=None):
        self.h_flicker = flicker_bit
        if amplitude is not None:
            self.h_flicker_amplitude = amplitude

    def set_v_flicker(self, flicker_bit, amplitude=None):
        self.v_flicker = flicker_bit
        if amplitude is not None:
            self.v_flicker_amplitude = amplitude

    # *********************************************************************************************
    #  BASIC ANIMATION METHODS
    # *********************************************************************************************
    def close_eyes(
        self, left=True, right=True
    ):  # Renamed from close to avoid conflict with file close
        if left:
            self.eyeL_height_next = 1
            self.eyeL_open = False
        if right:
            self.eyeR_height_next = 1
            self.eyeR_open = False

    def open_eyes(self, left=True, right=True):  # Renamed from open
        if left:
            self.eyeL_open = True
        if right:
            self.eyeR_open = True

    def blink(self, left=True, right=True):
        self.close_eyes(left, right)
        self.open_eyes(left, right)

    # *********************************************************************************************
    #  MACRO ANIMATION METHODS
    # *********************************************************************************************
    def anim_confused(self):
        self.confused = True
        self.confused_animation_timer = time.monotonic()  # Reset timer

    def anim_laugh(self):
        self.laugh = True
        self.laugh_animation_timer = time.monotonic()  # Reset timer

    # *********************************************************************************************
    #  PRE-CALCULATIONS AND ACTUAL DRAWINGS
    # *********************************************************************************************
    def draw_eyes(self):  # Renamed from drawEyes
        # PRE-CALCULATIONS - EYE SIZES AND VALUES FOR ANIMATION TWEENINGS
        current_time = time.monotonic()

        if self.curious:
            if self.eyeL_x_next <= 10:
                self.eyeL_height_offset = 8
            elif (
                self.eyeL_x_next >= (self.get_screen_constraint_X() - 10)
                and self.cyclops
            ):
                self.eyeL_height_offset = 8
            else:
                self.eyeL_height_offset = 0

            if (
                self.eyeR_x_next >= self.screen_width - self.eyeR_width_current - 10
            ):  # Assuming eyeRxNext is calculated before this
                self.eyeR_height_offset = 8
            else:
                self.eyeR_height_offset = 0
        else:
            self.eyeL_height_offset = 0
            self.eyeR_height_offset = 0

        # Left eye height
        self.eyeL_height_current = (
            self.eyeL_height_current + self.eyeL_height_next + self.eyeL_height_offset
        ) // 2
        self.eyeL_y += (self.eyeL_height_default - self.eyeL_height_current) // 2
        self.eyeL_y -= self.eyeL_height_offset // 2
        # Right eye height
        self.eyeR_height_current = (
            self.eyeR_height_current + self.eyeR_height_next + self.eyeR_height_offset
        ) // 2
        self.eyeR_y += (self.eyeR_height_default - self.eyeR_height_current) // 2
        self.eyeR_y -= self.eyeR_height_offset // 2

        if self.eyeL_open:
            if self.eyeL_height_current <= 1 + self.eyeL_height_offset:
                self.eyeL_height_next = self.eyeL_height_default
        if self.eyeR_open:
            if self.eyeR_height_current <= 1 + self.eyeR_height_offset:
                self.eyeR_height_next = self.eyeR_height_default

        self.eyeL_width_current = (self.eyeL_width_current + self.eyeL_width_next) // 2
        self.eyeR_width_current = (self.eyeR_width_current + self.eyeR_width_next) // 2
        self.spaceBetween_current = (
            self.spaceBetween_current + self.spaceBetween_next
        ) // 2

        self.eyeL_x = (self.eyeL_x + self.eyeL_x_next) // 2
        self.eyeL_y = (self.eyeL_y + self.eyeL_y_next) // 2

        self.eyeR_x_next = (
            self.eyeL_x_next + self.eyeL_width_current + self.spaceBetween_current
        )
        self.eyeR_y_next = self.eyeL_y_next
        self.eyeR_x = (self.eyeR_x + self.eyeR_x_next) // 2
        self.eyeR_y = (self.eyeR_y + self.eyeR_y_next) // 2

        self.eyeL_border_radius_current = (
            self.eyeL_border_radius_current + self.eyeL_border_radius_next
        ) // 2
        self.eyeR_border_radius_current = (
            self.eyeR_border_radius_current + self.eyeR_border_radius_next
        ) // 2

        # APPLYING MACRO ANIMATIONS
        if self.autoblinker:
            if current_time >= self.blinktimer:
                self.blink()
                self.blinktimer = (
                    current_time
                    + (self.blink_interval)
                    + (
                        random.randrange(self.blink_interval_variation)
                        if self.blink_interval_variation > 0
                        else 0
                    )
                )

        if self.laugh:
            if self.laugh_toggle:
                self.set_v_flicker(True, 5)
                self.laugh_animation_timer = current_time
                self.laugh_toggle = False
            elif (
                current_time
                >= self.laugh_animation_timer + self.laugh_animation_duration
            ):
                self.set_v_flicker(False, 0)
                self.laugh_toggle = True
                self.laugh = False

        if self.confused:
            if self.confused_toggle:
                self.set_h_flicker(True, 20)
                self.confused_animation_timer = current_time
                self.confused_toggle = False
            elif (
                current_time
                >= self.confused_animation_timer + self.confused_animation_duration
            ):
                self.set_h_flicker(False, 0)
                self.confused_toggle = True
                self.confused = False

        if self.idle:
            if current_time >= self.idle_animation_timer:
                constraint_x = self.get_screen_constraint_X()
                constraint_y = self.get_screen_constraint_Y()
                if constraint_x > 0:
                    self.eyeL_x_next = random.randint(
                        0, int(constraint_x)
                    )  # Convert to int
                if constraint_y > 0:
                    self.eyeL_y_next = random.randint(
                        0, int(constraint_y)
                    )  # Convert to int
                self.idle_animation_timer = (
                    current_time
                    + (self.idle_interval)
                    + (
                        random.randrange(self.idle_interval_variation)
                        if self.idle_interval_variation > 0
                        else 0
                    )
                )

        eyeL_x_draw = self.eyeL_x
        eyeR_x_draw = self.eyeR_x
        eyeL_y_draw = self.eyeL_y
        eyeR_y_draw = self.eyeR_y

        if self.h_flicker:
            if self.h_flicker_alternate:
                eyeL_x_draw += self.h_flicker_amplitude
                eyeR_x_draw += self.h_flicker_amplitude
            else:
                eyeL_x_draw -= self.h_flicker_amplitude
                eyeR_x_draw -= self.h_flicker_amplitude
            self.h_flicker_alternate = not self.h_flicker_alternate

        if self.v_flicker:
            if self.v_flicker_alternate:
                eyeL_y_draw += self.v_flicker_amplitude
                eyeR_y_draw += self.v_flicker_amplitude
            else:
                eyeL_y_draw -= self.v_flicker_amplitude
                eyeR_y_draw -= self.v_flicker_amplitude
            self.v_flicker_alternate = not self.v_flicker_alternate

        # Correctly implement cyclops mode by modifying instance attributes
        # This follows the C++ logic where attributes are changed before drawing
        # and affects subsequent calculations if these attributes are used (e.g., constraints)
        if self.cyclops:
            self.eyeR_width_current = 0
            self.eyeR_height_current = 0
            self.spaceBetween_current = 0  # Match C++ behavior

        # ACTUAL DRAWINGS
        self.draw.rectangle(
            [(0, 0), (self.screen_width, self.screen_height)], fill=BGCOLOR
        )  # Clear screen

        # Ensure all coordinates and dimensions are integers before drawing
        eyeL_x_draw_int = int(eyeL_x_draw)
        eyeL_y_draw_int = int(eyeL_y_draw)
        eyeL_width_current_int = int(self.eyeL_width_current)
        eyeL_height_current_int = int(self.eyeL_height_current)
        eyeL_border_radius_current_int = int(self.eyeL_border_radius_current)

        eyeR_x_draw_int = int(eyeR_x_draw)
        eyeR_y_draw_int = int(eyeR_y_draw)
        eyeR_width_current_int = int(self.eyeR_width_current)
        eyeR_height_current_int = int(self.eyeR_height_current)
        eyeR_border_radius_current_int = int(self.eyeR_border_radius_current)

        # Draw basic eye rectangles
        # Pillow's rounded_rectangle takes (x0, y0, x1, y1)
        self.draw.rounded_rectangle(
            (
                eyeL_x_draw_int,
                eyeL_y_draw_int,
                eyeL_x_draw_int + eyeL_width_current_int,
                eyeL_y_draw_int + eyeL_height_current_int,
            ),
            radius=eyeL_border_radius_current_int,
            fill=MAINCOLOR,
        )
        if not self.cyclops:
            self.draw.rounded_rectangle(
                (
                    eyeR_x_draw_int,
                    eyeR_y_draw_int,
                    eyeR_x_draw_int + eyeR_width_current_int,
                    eyeR_y_draw_int + eyeR_height_current_int,
                ),
                radius=eyeR_border_radius_current_int,
                fill=MAINCOLOR,
            )

        # Prepare mood type transitions
        if self.tired:
            self.eyelids_tired_height_next = self.eyeL_height_current // 2
            self.eyelids_angry_height_next = 0
        else:
            self.eyelids_tired_height_next = 0

        if self.angry:
            self.eyelids_angry_height_next = self.eyeL_height_current // 2
            self.eyelids_tired_height_next = 0
        else:
            self.eyelids_angry_height_next = 0

        if self.happy:
            self.eyelids_happy_bottom_offset_next = self.eyeL_height_current // 2
        else:
            self.eyelids_happy_bottom_offset_next = 0

        # Draw tired top eyelids
        self.eyelids_tired_height = (
            self.eyelids_tired_height + self.eyelids_tired_height_next
        ) // 2
        if self.eyelids_tired_height > 0:  # Only draw if there's something to draw
            if not self.cyclops:
                # Left eye
                self.draw.polygon(
                    [
                        (eyeL_x_draw_int, eyeL_y_draw_int - 1),
                        (eyeL_x_draw_int + eyeL_width_current_int, eyeL_y_draw_int - 1),
                        (
                            eyeL_x_draw_int,
                            eyeL_y_draw_int + int(self.eyelids_tired_height) - 1,
                        ),
                    ],
                    fill=BGCOLOR,
                )
                # Right eye
                self.draw.polygon(
                    [
                        (eyeR_x_draw_int, eyeR_y_draw_int - 1),
                        (eyeR_x_draw_int + eyeR_width_current_int, eyeR_y_draw_int - 1),
                        (
                            eyeR_x_draw_int + eyeR_width_current_int,
                            eyeR_y_draw_int + int(self.eyelids_tired_height) - 1,
                        ),
                    ],
                    fill=BGCOLOR,
                )
            else:  # Cyclops
                # Left half
                self.draw.polygon(
                    [
                        (eyeL_x_draw_int, eyeL_y_draw_int - 1),
                        (
                            eyeL_x_draw_int + (eyeL_width_current_int // 2),
                            eyeL_y_draw_int - 1,
                        ),
                        (
                            eyeL_x_draw_int,
                            eyeL_y_draw_int + int(self.eyelids_tired_height) - 1,
                        ),
                    ],
                    fill=BGCOLOR,
                )
                # Right half
                self.draw.polygon(
                    [
                        (
                            eyeL_x_draw_int + (eyeL_width_current_int // 2),
                            eyeL_y_draw_int - 1,
                        ),
                        (eyeL_x_draw_int + eyeL_width_current_int, eyeL_y_draw_int - 1),
                        (
                            eyeL_x_draw_int + eyeL_width_current_int,
                            eyeL_y_draw_int + int(self.eyelids_tired_height) - 1,
                        ),
                    ],
                    fill=BGCOLOR,
                )

        # Draw angry top eyelids
        self.eyelids_angry_height = (
            self.eyelids_angry_height + self.eyelids_angry_height_next
        ) // 2
        if self.eyelids_angry_height > 0:
            if not self.cyclops:
                # Left eye
                self.draw.polygon(
                    [
                        (eyeL_x_draw_int, eyeL_y_draw_int - 1),
                        (eyeL_x_draw_int + eyeL_width_current_int, eyeL_y_draw_int - 1),
                        (
                            eyeL_x_draw_int + eyeL_width_current_int,
                            eyeL_y_draw_int + int(self.eyelids_angry_height) - 1,
                        ),
                    ],
                    fill=BGCOLOR,
                )
                # Right eye
                self.draw.polygon(
                    [
                        (eyeR_x_draw_int, eyeR_y_draw_int - 1),
                        (eyeR_x_draw_int + eyeR_width_current_int, eyeR_y_draw_int - 1),
                        (
                            eyeR_x_draw_int,
                            eyeR_y_draw_int + int(self.eyelids_angry_height) - 1,
                        ),
                    ],
                    fill=BGCOLOR,
                )
            else:  # Cyclops
                # Left half
                self.draw.polygon(
                    [
                        (eyeL_x_draw_int, eyeL_y_draw_int - 1),
                        (
                            eyeL_x_draw_int + (eyeL_width_current_int // 2),
                            eyeL_y_draw_int - 1,
                        ),
                        (
                            eyeL_x_draw_int + (eyeL_width_current_int // 2),
                            eyeL_y_draw_int + int(self.eyelids_angry_height) - 1,
                        ),
                    ],
                    fill=BGCOLOR,
                )
                # Right half
                self.draw.polygon(
                    [
                        (
                            eyeL_x_draw_int + (eyeL_width_current_int // 2),
                            eyeL_y_draw_int - 1,
                        ),
                        (eyeL_x_draw_int + eyeL_width_current_int, eyeL_y_draw_int - 1),
                        (
                            eyeL_x_draw_int + (eyeL_width_current_int // 2),
                            eyeL_y_draw_int + int(self.eyelids_angry_height) - 1,
                        ),
                    ],
                    fill=BGCOLOR,
                )

        # Draw happy bottom eyelids
        self.eyelids_happy_bottom_offset = (
            self.eyelids_happy_bottom_offset + self.eyelids_happy_bottom_offset_next
        ) // 2
        if self.eyelids_happy_bottom_offset > 0:
            eyelids_happy_bottom_offset_int = int(self.eyelids_happy_bottom_offset)
            # Left eye
            self.draw.rounded_rectangle(
                (
                    eyeL_x_draw_int - 1,
                    (eyeL_y_draw_int + eyeL_height_current_int)
                    - eyelids_happy_bottom_offset_int
                    + 1,
                    eyeL_x_draw_int + eyeL_width_current_int + 1,
                    eyeL_y_draw_int
                    + eyeL_height_current_int
                    + int(self.eyeL_height_default),
                ),  # Ends well below the eye
                radius=eyeL_border_radius_current_int,
                fill=BGCOLOR,
            )
            if not self.cyclops:
                # Right eye
                self.draw.rounded_rectangle(
                    (
                        eyeR_x_draw_int - 1,
                        (eyeR_y_draw_int + eyeR_height_current_int)
                        - eyelids_happy_bottom_offset_int
                        + 1,
                        eyeR_x_draw_int + eyeR_width_current_int + 1,
                        eyeR_y_draw_int
                        + eyeR_height_current_int
                        + int(self.eyeR_height_default),
                    ),
                    radius=eyeR_border_radius_current_int,
                    fill=BGCOLOR,
                )

        # self.image.save(f"debug_frame_{int(current_time*100)}.png") # For debugging
