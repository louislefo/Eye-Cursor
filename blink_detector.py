import math

class BlinkDetector:
    """
    Detects eye blinks based on the Eye Aspect Ratio (EAR).
    Uses MediaPipe Face Mesh landmarks.
    """
    # MediaPipe Face Mesh Indices
    # Left Eye: [362, 385, 387, 263, 373, 380]
    LEFT_EYE = [362, 385, 387, 263, 373, 380]
    # Right Eye: [33, 160, 158, 133, 153, 144]
    RIGHT_EYE = [33, 160, 158, 133, 153, 144]

    def __init__(self, ear_threshold=0.2, consecutive_frames=2):
        """
        Initialize the BlinkDetector.

        Args:
            ear_threshold (float): EAR value below which a blink is detected.
            consecutive_frames (int): Number of consecutive frames under threshold to register a blink.
        """
        self.ear_threshold = ear_threshold
        self.consecutive_frames = consecutive_frames
        self.blink_counter = 0
        self.total_blinks = 0
        self.current_ear = 0.0

    def _calculate_distance(self, p1, p2):
        """Calculates Euclidean distance between two points."""
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def _calculate_ear(self, eye):
        """
        Calculates the Eye Aspect Ratio (EAR) for a given eye.
        
        Args:
            eye (list): List of (x, y) coordinates for the 6 eye landmarks.
        
        Returns:
            float: The calculated EAR value.
        """
        # Vertical distances
        A = self._calculate_distance(eye[1], eye[5])
        B = self._calculate_distance(eye[2], eye[4])

        # Horizontal distance
        C = self._calculate_distance(eye[0], eye[3])

        if C == 0:
            return 0
            
        ear = (A + B) / (2.0 * C)
        return ear

    def detect_blink(self, landmarks):
        """
        Processes facial landmarks to detect blinks.

        Args:
            landmarks: MediaPipe NormalizedLandmarkList.

        Returns:
            str: "click" if a blink (wink/blink) is detected causing a trigger, None otherwise.
        """
        # Extract eye coordinates
        left_eye_pts = [(landmarks.landmark[i].x, landmarks.landmark[i].y) for i in self.LEFT_EYE]
        right_eye_pts = [(landmarks.landmark[i].x, landmarks.landmark[i].y) for i in self.RIGHT_EYE]

        leftEAR = self._calculate_ear(left_eye_pts)
        rightEAR = self._calculate_ear(right_eye_pts)

        # Average EAR
        ear = (leftEAR + rightEAR) / 2.0
        self.current_ear = ear

        # Blink logic
        if ear < self.ear_threshold:
            self.blink_counter += 1
        else:
            if self.blink_counter >= self.consecutive_frames:
                self.total_blinks += 1
                self.blink_counter = 0
                return "click"
            self.blink_counter = 0
        
        return None
