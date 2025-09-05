#!/usr/bin/env python3
"""
Camera Test Script
Simple script to test camera access and help diagnose issues.
"""

import cv2
import sys


def test_camera():
    """Test camera access and display basic info."""
    print("Testing camera access...")
    
    # Test multiple camera indices
    for i in range(5):  # Test indices 0-4
        print(f"\nTrying camera index {i}:")
        
        cap = cv2.VideoCapture(i)
        
        if cap.isOpened():
            print(f"  ✓ Camera {i} opened successfully")
            
            # Try to read a frame
            ret, frame = cap.read()
            if ret:
                height, width, channels = frame.shape
                print(f"  ✓ Frame read successfully: {width}x{height} with {channels} channels")
                
                # Show the frame briefly
                cv2.imshow(f'Camera {i} Test', frame)
                print(f"  ✓ Displaying camera {i} feed. Press any key to continue...")
                cv2.waitKey(2000)  # Show for 2 seconds
                cv2.destroyAllWindows()
                
            else:
                print(f"  ✗ Could not read frame from camera {i}")
            
            cap.release()
        else:
            print(f"  ✗ Could not open camera {i}")
    
    print("\nCamera test completed!")
    print("\nIf no cameras worked, please:")
    print("1. Check System Preferences > Security & Privacy > Camera")
    print("2. Make sure Python has camera permissions")
    print("3. Close other applications that might be using the camera")
    print("4. Try reconnecting your camera if it's external")


if __name__ == "__main__":
    test_camera()
