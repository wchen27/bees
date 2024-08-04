import cv2
from pupil_apriltags import Detector
from gateController import GateController

def detect_apriltags(camera_source=0, com_port='COM3'):
    # Initialize gate controller
    gc = GateController(com_port)
    gc.close_gate()

    # Initialize video input device
    cap = cv2.VideoCapture(camera_source)
    if not cap.isOpened():
        print("Error: Could not open video source.")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

    # Initialize AprilTag detector
    detector = Detector(families='tag36h11')

    cv2.namedWindow("AprilTag Detection")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        tags = detector.detect(gray)

        if tags:
            for tag in tags:
                print(f"Detected tag ID: {tag.tag_id}")
                if gc.door_status == 0:
                    gc.open_gate()
                    print("Found bee, open gate!")
        else:
            if gc.door_status == 1:
                gc.close_gate()
                print("Bee is gone, close gate!")

        cv2.imshow("AprilTag Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    gc.close_gate()
    gc.delete()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AprilTag Detection and Gate Control")
    parser.add_argument('--camera_source', type=int, default=0, help='Camera source (default: 0)')
    parser.add_argument('--com_port', type=str, default='COM3', help='COM port for gate controller (default: COM3)')
    args = parser.parse_args()

    detect_apriltags(args.camera_source, args.com_port)
