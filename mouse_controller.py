import pyautogui

class MouseController:
    """
    Wrapper for PyAutoGUI to control the mouse cursor.
    """
    def __init__(self):
        # Disable FailSafe to prevent crashes when cursor touches screen corners
        # Be careful when using this!
        pyautogui.FAILSAFE = False
        self.screen_w, self.screen_h = pyautogui.size()

    def move(self, coords):
        """
        Moves the mouse cursor to the specified coordinates.
        Clamps coordinates to screen boundaries to avoid errors.

        Args:
            coords (tuple): (x, y) target coordinates.
        """
        if coords is None:
            return
            
        x, y = coords
        
        # Clamp to screen size to ensure we stay within bounds
        # Subtracting 1 to be safe (0-indexed)
        x = max(0, min(x, self.screen_w - 1))
        y = max(0, min(y, self.screen_h - 1))
        
        try:
            pyautogui.moveTo(x, y)
        except pyautogui.FailSafeException:
            pass

    def click(self):
        """Performs a left mouse click."""
        pyautogui.click()
