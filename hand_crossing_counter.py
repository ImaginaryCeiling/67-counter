#!/usr/bin/env python3
"""
Hand Crossing Counter
Tracks the number of times your left hand passes your right hand vertically.
"""

import cv2
import mediapipe as mp
import numpy as np
import time
from datetime import datetime


class HandCrossingCounter:
    def __init__(self):
        # Initialize MediaPipe hands
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_draw = mp.solutions.drawing_utils
        
        # Tracking variables
        self.crossing_count = 0
        self.left_hand_y = None
        self.right_hand_y = None
        self.previous_left_y = None
        self.previous_right_y = None
        self.last_crossing_time = 0
        self.crossing_cooldown = 0.5  # Prevent multiple counts for same crossing
        
        # Display settings
        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.font_scale = 1
        self.thickness = 2
        
        print("Hand Crossing Counter initialized!")
        print("Controls:")
        print("- 'r' to reset counter")
        print("- 's' to save results")
        print("- 'q' to quit")
    
    def get_hand_position(self, landmarks, hand_label):
        """Extract the center position of a hand from landmarks."""
        if landmarks:
            # Use the middle finger MCP (joint 9) as hand center
            x = landmarks.landmark[9].x
            y = landmarks.landmark[9].y
            return x, y
        return None, None
    
    def detect_crossing(self, current_time):
        """Detect if left hand crosses right hand vertically."""
        if (self.left_hand_y is not None and self.right_hand_y is not None and
            self.previous_left_y is not None and self.previous_right_y is not None):
            
            # Check if hands crossed vertically
            crossed_now = (self.left_hand_y < self.right_hand_y and 
                          self.previous_left_y > self.previous_right_y) or \
                         (self.left_hand_y > self.right_hand_y and 
                          self.previous_left_y < self.previous_right_y)
            
            # Apply cooldown to prevent multiple counts
            if crossed_now and (current_time - self.last_crossing_time) > self.crossing_cooldown:
                self.crossing_count += 1
                self.last_crossing_time = current_time
                print(f"Crossing detected! Count: {self.crossing_count}")
                return True
        
        return False
    
    def draw_ui(self, image):
        """Draw the user interface on the image."""
        height, width = image.shape[:2]
        
        # Draw counter
        counter_text = f"Crossings: {self.crossing_count}"
        cv2.putText(image, counter_text, (20, 50), self.font, self.font_scale, 
                   (0, 255, 0), self.thickness)
        
        # Draw hand positions if detected
        if self.left_hand_y is not None:
            left_text = f"Left Y: {self.left_hand_y:.2f}"
            cv2.putText(image, left_text, (20, 100), self.font, 0.6, 
                       (255, 0, 0), 2)
        
        if self.right_hand_y is not None:
            right_text = f"Right Y: {self.right_hand_y:.2f}"
            cv2.putText(image, right_text, (20, 130), self.font, 0.6, 
                       (0, 0, 255), 2)
        
        # Draw instructions
        instructions = [
            "Controls:",
            "'r' - Reset counter",
            "'s' - Save results", 
            "'q' - Quit"
        ]
        
        for i, instruction in enumerate(instructions):
            cv2.putText(image, instruction, (width - 250, 30 + i * 25), 
                       self.font, 0.5, (255, 255, 255), 1)
        
        # Draw horizontal line at center for reference
        cv2.line(image, (0, height // 2), (width, height // 2), (100, 100, 100), 1)
        
        return image
    
    def save_results(self):
        """Save the current results to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"crossing_results_{timestamp}.txt"
        
        try:
            with open(filename, 'w') as f:
                f.write(f"Hand Crossing Counter Results\n")
                f.write(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Crossings: {self.crossing_count}\n")
            
            print(f"Results saved to {filename}")
        except Exception as e:
            print(f"Error saving results: {e}")
    
    def reset_counter(self):
        """Reset the crossing counter."""
        self.crossing_count = 0
        self.last_crossing_time = 0
        print("Counter reset to 0")
    
    def run(self):
        """Main execution loop."""
        # Try different camera indices
        cap = None
        camera_indices = [0, 1, 2]  # Try multiple camera sources
        
        for i in camera_indices:
            print(f"Trying camera index {i}...")
            test_cap = cv2.VideoCapture(i)
            if test_cap.isOpened():
                # Test if we can actually read a frame
                ret, test_frame = test_cap.read()
                if ret:
                    print(f"Successfully opened camera at index {i}")
                    cap = test_cap
                    break
                else:
                    test_cap.release()
            else:
                test_cap.release()
        
        if cap is None:
            print("Error: Could not open any camera")
            print("Please check:")
            print("1. Camera permissions in System Preferences > Security & Privacy > Camera")
            print("2. No other applications are using the camera")
            print("3. Camera is properly connected")
            return
        
        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
        
        print("Starting hand tracking... Position your hands in front of the camera")
        print("Make sure to allow camera access if prompted by macOS")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    print("Error: Could not read frame")
                    break
                
                # Flip frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process frame with MediaPipe
                results = self.hands.process(rgb_frame)
                
                # Store previous positions
                self.previous_left_y = self.left_hand_y
                self.previous_right_y = self.right_hand_y
                
                # Reset current positions
                self.left_hand_y = None
                self.right_hand_y = None
                
                # Process detected hands
                if results.multi_hand_landmarks and results.multi_handedness:
                    for landmarks, handedness in zip(results.multi_hand_landmarks, 
                                                    results.multi_handedness):
                        # Draw hand landmarks
                        self.mp_draw.draw_landmarks(frame, landmarks, 
                                                  self.mp_hands.HAND_CONNECTIONS)
                        
                        # Determine if this is left or right hand
                        hand_label = handedness.classification[0].label
                        
                        # Get hand position
                        x, y = self.get_hand_position(landmarks, hand_label)
                        
                        if x is not None and y is not None:
                            # Draw hand center
                            center_x = int(x * frame.shape[1])
                            center_y = int(y * frame.shape[0])
                            color = (255, 0, 0) if hand_label == "Left" else (0, 0, 255)
                            cv2.circle(frame, (center_x, center_y), 10, color, -1)
                            
                            # Store y position (note: MediaPipe uses "Left" for right hand in mirror)
                            if hand_label == "Left":  # This is actually the right hand in mirror
                                self.right_hand_y = y
                            else:  # This is actually the left hand in mirror
                                self.left_hand_y = y
                
                # Detect crossings
                current_time = time.time()
                crossing_detected = self.detect_crossing(current_time)
                
                # Draw UI
                frame = self.draw_ui(frame)
                
                # Show frame
                cv2.imshow('Hand Crossing Counter', frame)
                
                # Handle keyboard input
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
                elif key == ord('r'):
                    self.reset_counter()
                elif key == ord('s'):
                    self.save_results()
        
        except KeyboardInterrupt:
            print("\nProgram interrupted by user")
        
        finally:
            cap.release()
            cv2.destroyAllWindows()
            print(f"Final crossing count: {self.crossing_count}")


def main():
    """Main function to run the hand crossing counter."""
    counter = HandCrossingCounter()
    counter.run()


if __name__ == "__main__":
    main()
