import time
import numpy as np
import cv2
from gateController import GateController

def main():
    # Set user settings
    threshold1 = 6000  # Threshold to open the gate
    threshold2 = 1500  # Threshold to close the gate

    # Select waiting zone 1
    xmin1, ymin1, width1, height1 = 200, 600, 640, 640

    # Select waiting zone 2
    xmin2, ymin2, width2, height2 = 2200, 600, 640, 640

    # Initialize gate controller and camera
    gc = GateController('COM3')

    gc.close_gate()
    gate_is_closed = True

    cap = cv2.VideoCapture(0)  # Adjust the camera source if needed

    if not cap.isOpened():
        print("Error: Could not open video source.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 2640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height1)

    # Default values
    image_mean_bg_calculated = 220
    num_of_black_pixels_bg_calculated = 3700

    # Display the captured image. Open/close the gate based on thresholds and default values
    cv2.namedWindow("Gate Controller")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        roi1 = frame[ymin1:ymin1+height1, xmin1:xmin1+width1]
        roi2 = frame[ymin2:ymin2+height2, xmin2:xmin2+width2]

        gray1 = cv2.cvtColor(roi1, cv2.COLOR_BGR2GRAY)
        gray2 = cv2.cvtColor(roi2, cv2.COLOR_BGR2GRAY)

        _, thresh1 = cv2.threshold(gray1, 30, 60, cv2.THRESH_BINARY_INV)
        _, thresh2 = cv2.threshold(gray2, 30, 60, cv2.THRESH_BINARY_INV)

        num_of_black_pixels_wz1 = np.sum(thresh1 == 255)
        num_of_black_pixels_wz2 = np.sum(thresh2 == 255)

        if num_of_black_pixels_wz1 >= num_of_black_pixels_bg_calculated + threshold1:
            # bee in waiting zone 1
            if 'tic_wz1' not in locals():
                tic_wz1 = time.time()
            else:
                time_in_wz1 = time.time() - tic_wz1
                if time_in_wz1 >= 1:
                    if gate_is_closed:
                        gc.open_gate()
                        gate_is_closed = False
        elif num_of_black_pixels_wz1 <= num_of_black_pixels_bg_calculated + threshold2:
            # bee left waiting zone 1
            if 'tic_wz1' in locals():
                del tic_wz1
            if not gate_is_closed:
                gc.close_gate()
                gate_is_closed = True

        if num_of_black_pixels_wz2 >= num_of_black_pixels_bg_calculated + threshold1:
            # bee in waiting zone 2
            if 'tic_wz2' not in locals():
                tic_wz2 = time.time()
            else:
                time_in_wz2 = time.time() - tic_wz2
                if time_in_wz2 >= 1:
                    if gate_is_closed:
                        gc.open_gate()
                        gate_is_closed = False
        elif num_of_black_pixels_wz2 <= num_of_black_pixels_bg_calculated + threshold2:
            # bee left waiting zone 2
            if 'tic_wz2' in locals():
                del tic_wz2
            if not gate_is_closed:
                gc.close_gate()
                gate_is_closed = True

        cv2.imshow("Gate Controller", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    gc.close_gate()
    gc.delete()

if __name__ == "__main__":
    main()
