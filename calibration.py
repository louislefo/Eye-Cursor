import cv2
import numpy as np

class Calibration:
    """
    Handles the calibration process to map eye gaze to screen coordinates.
    Uses homography to transform eye space coordinates to screen space.
    """
    def __init__(self):
        self.calibration_points = [] # Points on screen (x, y)
        self.eye_points = []         # Corresponding eye features (x, y)
        self.homography_matrix = None
        self.is_calibrated = False

    def add_point(self, screen_point, eye_point):
        """
        Adds a calibration point pair (screen coordinate and corresponding eye coordinate).

        Args:
            screen_point (tuple): (x, y) coordinates on the screen.
            eye_point (tuple): (x, y) coordinates of the eye/gaze.
        """
        self.calibration_points.append(screen_point)
        self.eye_points.append(eye_point)

    def calculate_homography(self):
        """
        Calculates the homography matrix from the collected calibration points.
        Requires at least 4 points.
        
        Returns:
            bool: True if calibration was successful, False otherwise.
        """
        if len(self.calibration_points) < 4:
            print("Not enough points for calibration (min 4 required)")
            return False

        src_pts = np.array(self.eye_points).reshape(-1, 1, 2)
        dst_pts = np.array(self.calibration_points).reshape(-1, 1, 2)

        # Calculate Homography
        # cv2.RANSAC helps to exclude outliers
        self.homography_matrix, _ = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        
        if self.homography_matrix is not None:
             self.is_calibrated = True
             print("Calibration successful!")
             return True
        else:
             print("Calibration failed to compute homography.")
             return False

    def map_gaze(self, eye_point):
        """
        Maps an eye point to screen coordinates using the calculated homography matrix.

        Args:
            eye_point (tuple): (x, y) coordinates of the eye/gaze.

        Returns:
            tuple or None: (x, y) screen coordinates, or None if not calibrated/mapping failed.
        """
        if not self.is_calibrated or self.homography_matrix is None:
            return None

        # Convert to homogeneous coordinates [x, y, 1]
        src_pt = np.array([eye_point[0], eye_point[1], 1]).reshape(3, 1)
        
        # Apply homography
        dst_pt = np.dot(self.homography_matrix, src_pt)
        
        # Normalize (convert back from homogeneous coordinates)
        if dst_pt[2] != 0:
            x = int(dst_pt[0] / dst_pt[2])
            y = int(dst_pt[1] / dst_pt[2])
            return (x, y)
        return None

    def reset(self):
        """
        Resets the calibration data and status.
        Use this to start a new calibration session.
        """
        self.calibration_points = []
        self.eye_points = []
        self.homography_matrix = None
        self.is_calibrated = False
