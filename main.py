import cv2
import pyautogui
from vision_engine import VisionEngine
from gaze_tracker import GazeTracker
from blink_detector import BlinkDetector
from mouse_controller import MouseController
from calibration import Calibration

def main():
    """
    Main execution loop for IrisPoint & BlinkClick.
    Handles camera input, computer vision processing, and state management (Calibration vs Tracking).
    """
    # --- Initialization ---
    vision = VisionEngine()
    gaze = GazeTracker()
    blink = BlinkDetector()
    mouse = MouseController()
    calibration = Calibration()
    
    # --- Calibration Setup ---
    screen_w, screen_h = pyautogui.size()
    # Define a 3x3 grid for calibration points
    calibration_points = [
        (20, 20), (screen_w//2, 20), (screen_w-20, 20),
        (20, screen_h//2), (screen_w//2, screen_h//2), (screen_w-20, screen_h//2),
        (20, screen_h-20), (screen_w//2, screen_h-20), (screen_w-20, screen_h-20)
    ]
    calib_idx = 0
    is_calibrating = True
    key_pressed_or_mouse = False

    # --- Mouse Callback (for Calibration triggers) ---
    def mouse_click_handler(event, x, y, flags, param):
        nonlocal key_pressed_or_mouse
        if event == cv2.EVENT_LBUTTONDOWN:
            key_pressed_or_mouse = True

    # --- Window Setup ---
    # Fullscreen window is best for accurate calibration
    cv2.namedWindow('IrisPoint & BlinkClick', cv2.WINDOW_NORMAL)
    cv2.setWindowProperty('IrisPoint & BlinkClick', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    cv2.setMouseCallback('IrisPoint & BlinkClick', mouse_click_handler)
    
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        key_pressed_or_mouse = False # Reset click flag per frame
        success, image = cap.read()
        if not success:
            continue

        # Flip image for mirror effect (more intuitive for user)
        # Note: MediaPipe needs RGB, but we work in BGR for OpenCV
        # The flip operation changes Left<->Right logic
        image = cv2.flip(image, 1) 
        
        frame_h, frame_w, _ = image.shape
        
        # --- Process Frame ---
        landmarks = vision.process_frame(image)
        
        if landmarks:
            # 1. Get Eye Centers
            left_iris, right_iris = vision.get_iris_centers(landmarks, image.shape)
            # Calculate midpoint of eyes for raw gaze tracking
            gaze_point_eye = ((left_iris[0] + right_iris[0]) / 2, (left_iris[1] + right_iris[1]) / 2)

            # 2. Blink Detection
            action = blink.detect_blink(landmarks)
            
            # Display EAR for debugging/feedback
            cv2.putText(image, f"EAR: {blink.current_ear:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            
            # Perform Click if blink detected
            if action == "click":
                mouse.click()
                cv2.putText(image, "BLINK CLICK!", (300, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # 3. State Machine: Calibration or Tracking
            key = cv2.waitKey(5) & 0xFF
            
            # 'c' key restarts calibration
            if key == ord('c') or key == ord('C'):
                is_calibrating = True
                calibration.reset()
                calib_idx = 0
                print("Restarting Calibration...")

            if is_calibrating:
                # --- Calibration Mode ---
                # Draw calibration target
                target_x, target_y = calibration_points[calib_idx]
                
                # Map screen coordinates to camera frame coordinates for display
                draw_x = int(target_x / screen_w * frame_w)
                draw_y = int(target_y / screen_h * frame_h)
                
                # Draw visual feedback
                cv2.circle(image, (draw_x, draw_y), 20, (0, 255, 255), -1) # Yellow outer
                cv2.circle(image, (draw_x, draw_y), 5, (0, 0, 255), -1)   # Red inner
                
                msg = f"Look at DOT {calib_idx+1}/{len(calibration_points)} -> CLICK or SPACE"
                cv2.putText(image, msg, (draw_x - 150, draw_y - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
                
                # Capture point on SPACE or Mouse Click
                if key == 32 or key_pressed_or_mouse: 
                    print(f"Captured point {calib_idx}")
                    calibration.add_point((target_x, target_y), gaze_point_eye)
                    calib_idx += 1
                    cv2.waitKey(200) # Debounce
                    
                    # Check if calibration is complete
                    if calib_idx >= len(calibration_points):
                        is_calibrating = False
                        success_calib = calibration.calculate_homography()
                        if success_calib:
                            print("Calibration Done")
                            cv2.destroyAllWindows() # Close calibration window
                            continue # Skip imshow for this frame

            elif calibration.is_calibrated:
                # --- Tracking Mode ---
                # Map raw eye coordinates to screen coordinates
                screen_point = calibration.map_gaze(gaze_point_eye)
                
                # Apply smoothing
                smoothed_point = gaze.smooth_gaze(screen_point)
                
                # Move mouse
                if smoothed_point:
                    mouse.move(smoothed_point)
                
                # In tracking mode, we don't show the window by default (headless feel)
                continue

            # --- Visual Debugging (only in Calibration or if window open) ---
            vision.draw_mesh(image, landmarks)
            cv2.circle(image, (int(left_iris[0]), int(left_iris[1])), 3, (0, 255, 0), -1)
            cv2.circle(image, (int(right_iris[0]), int(right_iris[1])), 3, (0, 255, 0), -1)

            if key == 27: # ESC to exit
                break

        else:
             # If no face detected, still allow exit
            if cv2.waitKey(5) & 0xFF == 27:
                break
        
        # Only show window if we are calibrating or not yet calibrated
        if not calibration.is_calibrated:
            try:
                cv2.imshow('IrisPoint & BlinkClick', image)
            except cv2.error:
                pass 

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
