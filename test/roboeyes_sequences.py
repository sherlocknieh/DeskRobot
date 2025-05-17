import time
import cv2
import numpy as np

from roboeyes import RoboEyes,DEFAULT, HAPPY, TIRED,N

def main():
    screen_width = 128
    screen_height = 64

    robo_eyes = RoboEyes(screen_width, screen_height, 10)
    robo_eyes.set_position(DEFAULT)  # Eye position should be middle center
    robo_eyes.close_eyes()  # Start with closed eyes

    # Define the sequence of events
    # Each event is a dictionary with:
    # - "time_offset": Time in seconds from the start of the sequence loop for this event to trigger.
    # - "action": A lambda function to execute.
    # - "description": A string to print when the event occurs.
    event_sequence = [
        {
            "time_offset": 2.0,
            "action": lambda: robo_eyes.open_eyes(),
            "description": "Event 1: Eyes opened",
        },
        {
            "time_offset": 4.0,
            "action": lambda: (robo_eyes.set_mood(HAPPY), robo_eyes.anim_laugh()),
            "description": "Event 2: Mood HAPPY, anim_laugh",
        },
        {
            "time_offset": 6.0,
            "action": lambda: robo_eyes.set_mood(TIRED),
            "description": "Event 3: Mood TIRED",
        },
        {
            "time_offset": 8.0,
            "action": lambda: (robo_eyes.anim_confused()),
            "description": "Event 3: anim_yawn, mood DEFAULT",
        },
        {
            "time_offset": 10.0,
            "action": lambda: (robo_eyes.close_eyes(), robo_eyes.set_mood(DEFAULT)),
            "description": "Event 4: Eyes closed, mood DEFAULT. Restarting sequence.",
        },
        # To add a new event, simply add a new dictionary here.
        # For example:
        # {
        #     "time_offset": 10.0, # Trigger after 10 seconds in the loop
        #     "action": lambda: robo_eyes.set_curiosity(True),
        #     "description": "Event 5: Set curious to True",
        # },
        # Then, the sequence would restart after this new event,
        # or you'd adjust the "reset" logic if the last event isn't the reset anymore.
        # If the last event is the reset, ensure its time_offset is the largest.
    ]

    event_timer_start = time.monotonic()  # Start event timer from here
    next_event_index = 0

    print("Starting RoboEyes animation sequence. Press 'q' to quit.")

    while True:
        current_time = time.monotonic()
        elapsed_time = current_time - event_timer_start

        # Check for the next event in the sequence
        if next_event_index < len(event_sequence):
            event = event_sequence[next_event_index]
            if elapsed_time >= event["time_offset"]:
                event["action"]()  # Execute the event's action
                print(event["description"])
                next_event_index += 1
        else:
            # All events in the sequence have been played, reset the sequence
            event_timer_start = time.monotonic()
            next_event_index = 0
            # The last event's description in event_sequence already indicates restarting.

        image = robo_eyes.update()

        if image:
            cv_image = np.array(image)
            cv_image = cv_image * 255  # Convert 0/1 image to 0/255
            cv_image = cv_image.astype(np.uint8)

            scale_factor = 4
            width = int(cv_image.shape[1] * scale_factor)
            height = int(cv_image.shape[0] * scale_factor)
            dim = (width, height)
            resized_cv_image = cv2.resize(
                cv_image, dim, interpolation=cv2.INTER_NEAREST
            )
            cv2.imshow("RoboEyes Animation Sequence", resized_cv_image)

        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

    cv2.destroyAllWindows()
    print("RoboEyes animation sequence stopped.")


if __name__ == "__main__":
    main()
