# Vision Games

This repository contains a collection of classic games implemented in Python, where the controls are driven entirely by hand and face gestures captured via a webcam. The project leverages **OpenCV** for image processing, **MediaPipe** for real-time tracking, and **PySide6 (Qt for Python)** for the graphical user interface.

## 👾 Games Included

* **🍉 Fruit Ninja (`ninja_game.py`)**: Use your hand as a sword to slice falling fruits (apples, bananas, grapes, and watermelons) while avoiding bombs.
* **✊✋✌️ Rock, Paper, Scissors (`rps_game.py`)**: Play a best-of-three match against the computer using hand gestures! Give a "thumbs up" (👍) to start a round, and then show Rock, Paper, or Scissors to the camera.
* **🚀 Face Dodge Multiplayer (`face_game.py`)**: Control a spaceship using your nose to dodge falling obstacles like rocks and meteors. Open your mouth to activate a temporary shield! You can play solo or in a 2-player local co-op mode.

### Prerequisites

* Python 3.10 or 3.11 installed.
* A connected webcam.

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/robertgvds/vision-games.git](https://github.com/robertgvds/vision-games.git)
    cd vision-games
    ```

2.  **Create and activate a virtual environment (Recommended):**

    Use your specific Python interpreter to create the environment, ensuring it's 3.10 or 3.11.

    *On macOS/Linux:*
    ```bash
    python3.10 -m venv venv
    # Or: python3.11 -m venv venv
    ```

    *On Windows (using the `py` launcher):*
    ```bash
    py -3.10 -m venv venv
    # Or: py -3.11 -m venv venv
    ```

    *Now, activate the environment:*

    *On Windows:*
    ```bash
    .\venv\Scripts\activate
    ```
    
    *On macOS/Linux:*
    ```bash
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    
    ```bash
    pip install opencv-python mediapipe pyside6
    ```

4.  **Run the application:**

    Make sure your virtual environment is activated, then run the script for the game you want to play:

    ```bash
    # To play Fruit Ninja
    python ninja_game.py

    # To play Rock, Paper, Scissors
    python rps_game.py

    # To play Face Dodge Multiplayer
    python face_game.py
    ```
