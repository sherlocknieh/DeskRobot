# mod_web_camera Project

This project is a Flask application that streams video from a camera using the Picamera2 library. It provides a simple web interface to view the camera feed in real-time.

## Features

- Real-time video streaming from a camera.
- Simple web interface built with Flask.
- Easy to set up and run.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd mod_web_camera
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

3. Ensure that you have the necessary hardware (e.g., a Raspberry Pi with a camera module).

## Usage

1. Run the application:
   ```
   python -m mod_web_camera.camera
   ```

2. Open your web browser and navigate to:
   ```
   http://localhost:5000/
   ```

3. You should see the camera feed displayed on the page.

## Requirements

- Python 3.x
- Flask
- OpenCV
- Picamera2

## License

This project is licensed under the MIT License.