import cv2 # OpenCV for image processing and RTSP stream handling
import threading # To run the camera feed in a separate thread to prevent lag
from ultralytics import YOLO # YOLOv8 framework for real-time object detection

class VisionSystem:
    def __init__(self, model_path="best.pt", camera_ip="192.168.1.64", username="admin", password="password123"):
        # Load the custom-trained YOLOv8 model and move it to the GPU (CUDA) for high-speed inference
        print("🚀 Loading YOLOv8s model to GPU...")
        self.model = YOLO(model_path).to('cuda')
        
        # Define the Hikvision RTSP stream URL. 
        # Using Channel 102 (Sub-stream) to reduce network load and latency.
        self.rtsp_url = f"rtsp://{username}:{password}@{camera_ip}:554/Streaming/Channels/102"
        
        # Initialize video capture with the RTSP URL
        self.cap = cv2.VideoCapture(self.rtsp_url)
        self.latest_frame = None # Store the most recent frame captured
        self.is_running = True # Control flag for the background thread
        
        # Start a background thread to continuously fetch frames. 
        # This prevents the frame buffer from building up and causing delay.
        self.thread = threading.Thread(target=self._update_frame, daemon=True)
        self.thread.start()

    def _update_frame(self):
        """Continuously capture frames in the background."""
        while self.is_running:
            success, frame = self.cap.read()
            if success:
                # Update the latest frame with the newest capture
                self.latest_frame = frame
            else:
                # If connection is lost, attempt to reconnect to the camera
                print("⚠️ Camera stream lost, attempting to reconnect...")
                self.cap.open(self.rtsp_url)

    def get_detections(self):
        """Perform inference on the latest frame and return formatted results."""
        if self.latest_frame is None:
            return [], None

        # Work on a copy of the latest frame to ensure data integrity
        frame = self.latest_frame.copy()
        
        # Run YOLO inference:
        # imgsz=640: Resizes input to 640x640 for optimized speed/accuracy balance
        # conf=0.5: Confidence threshold to filter out weak detections
        # half=True: Uses FP16 precision to significantly boost FPS on GTX 1650
        # verbose=False: Disables logs to keep the console clean for other data
        results = self.model.predict(frame, imgsz=640, conf=0.5, half=True, verbose=False)
        
        detections = []
        for r in results:
            for box in r.boxes:
                # Extract bounding box coordinates (x1, y1, x2, y2)
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                # Get the detected object's label name from the model's metadata
                label_id = int(box.cls[0])
                label_name = r.names[label_id]
                
                # Store normalized confidence score
                confidence = float(box.conf[0])
                
                # Append formatted result to the detection list
                detections.append({
                    'label': label_name,
                    'bbox': [int(x1), int(y1), int(x2), int(y2)],
                    'conf': confidence
                })

        return detections, frame

    def release(self):
        """Safe shutdown: stop thread and release camera resources."""
        self.is_running = False
        self.cap.release()