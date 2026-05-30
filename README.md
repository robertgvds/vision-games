This repository contains a collection of classic games implemented in Python, where the controls are driven entirely by hand gestures captured via a webcam. The project leverages **OpenCV** for image processing, **MediaPipe** for real-time hand tracking, and **PySide6 (Qt for Python)** for the graphical user interface.

## 👾 Games Included

* **Rock Paper Scissors (`rps_game.py`)**: Play the classic game against the computer using hand gestures.
* **Ninja Game (`ninja_game.py`)**: Slice fruits appearing on the screen using hand tracking.
* **Face Game (`face_game.py`)**: A dodging/interactive game using computer vision.

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

    *On Windows:*
    ```bash
    py -3.11 -m venv venv
    # If 'py' is not recognized, use: python -m venv venv
    ```

    *Now, activate the environment:*

    *On Windows:*
    ```bash
    .\venv\Scripts\activate
    ```
    *(Note: If you encounter an "execution of scripts is disabled" error in PowerShell, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` before activating).*
    
    *On macOS/Linux:*
    ```bash
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    
    > **Important:** The project requires a specific version of MediaPipe (`0.10.21`) to maintain compatibility with the `mp.solutions` API used in the code.

    ```bash
    pip install opencv-python mediapipe==0.10.21 pyside6
    ```

4.  **Run the application:**
    
    Choose one of the games and run its respective Python script. For example, to play Rock Paper Scissors:
    ```bash
    python rps_game.py
    ```