import cv2
import mediapipe as mp

class VisionEngine:
    """
    Handles video processing and face landmark extraction using MediaPipe Face Mesh.
    """
    
    # MediaPipe Iris Landmark Indices
    LEFT_IRIS_CENTER = 468
    RIGHT_IRIS_CENTER = 473

    def __init__(self):
        """Initializes the MediaPipe Face Mesh solution."""
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,  # Critical for iris landmarks
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def process_frame(self, image):
        """
        Processes a single video frame to find face landmarks.

        Args:
            image (numpy.ndarray): The input image frame (BGR).

        Returns:
            NormalizedLandmarkList or None: Detected face landmarks or None if no face found.
        """
        # Convert BGR -> RGB for MediaPipe
        image.flags.writeable = False
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(image_rgb)
        image.flags.writeable = True

        if results.multi_face_landmarks:
            return results.multi_face_landmarks[0]
        return None

    def draw_mesh(self, image, landmarks):
        """
        Draws the face mesh and iris connections on the image.

        Args:
            image (numpy.ndarray): The image to draw on.
            landmarks: The detected face landmarks.
        """
        # Draw face mesh tesselation
        mp.solutions.drawing_utils.draw_landmarks(
            image=image,
            landmark_list=landmarks,
            connections=self.mp_face_mesh.FACEMESH_TESSELATION,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_tesselation_style()
        )
        # Draw iris connections
        mp.solutions.drawing_utils.draw_landmarks(
            image=image,
            landmark_list=landmarks,
            connections=self.mp_face_mesh.FACEMESH_IRISES,
            landmark_drawing_spec=None,
            connection_drawing_spec=mp.solutions.drawing_styles.get_default_face_mesh_iris_connections_style()
        )

    def get_iris_centers(self, landmarks, image_shape):
        """
        Calculates the pixel coordinates of the left and right iris centers.

        Args:
            landmarks: The detected face landmarks.
            image_shape (tuple): The shape of the image (height, width, ...).

        Returns:
            tuple: ((left_x, left_y), (right_x, right_y)) coordinates.
        """
        h, w = image_shape[:2]
        
        left_iris = landmarks.landmark[self.LEFT_IRIS_CENTER]
        right_iris = landmarks.landmark[self.RIGHT_IRIS_CENTER]
        
        left_center = (left_iris.x * w, left_iris.y * h)
        right_center = (right_iris.x * w, right_iris.y * h)
        
        return left_center, right_center


