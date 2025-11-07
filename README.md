This repository contains a collection of classic games implemented in Python, where the controls are driven entirely by hand gestures captured via a webcam. The project leverages **OpenCV** for image processing, **MediaPipe** for real-time hand tracking, and **PySide6 (Qt for Python)** for the graphical user interface.

## 👾 Games Included

* 

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
    
    > ```bash
    > pip install opencv-python mediapipe pyside6
    > ```

4.  **Run the application:**
    
