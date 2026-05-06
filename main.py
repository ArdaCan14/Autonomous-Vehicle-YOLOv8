import cv2 # OpenCV for visualization
import time # For calculating FPS and handling timing
from detector import VisionSystem # Our custom YOLOv8 vision module
from brain import AutonomousBrain # Our logic and decision module
from networking import ESP32Comm # Our UDP communication bridge

def main():
    # --- INITIALIZATION PHASE ---
    # 1. Initialize the Vision System (Camera + YOLOv8 on GPU)
    # Ensure the model path and camera IP match your setup
    vision = VisionSystem(model_path="best.pt", camera_ip="192.168.1.64")
    
    # 2. Initialize the Brain (State management and decision logic)
    brain = AutonomousBrain()
    
    # 3. Initialize Networking (ESP32 communication)
    # 192.168.1.50 is the expected static IP of your ESP32 on the router
    net = ESP32Comm(esp32_ip="192.168.1.50")

    print("🚀 System Ready! Autonomous driving loop starting...")

    try:
        while True:
            # Mark the start time to calculate Frames Per Second (FPS)
            loop_start_time = time.time()

            # --- STEP 1: PERCEPTION (SEEING) ---
            # Get processed detections and the actual frame from the camera
            detections, frame = vision.get_detections()
            if frame is None:
                continue # Skip the loop if camera hasn't sent a frame yet

            # --- STEP 2: TELEMETRY (SENSING) ---
            # Check for distance data coming FROM the ESP32 (Ultrasonic Sensor)
            sensor_dist = net.receive_distance()
            if sensor_dist:
                # Update the brain with real-world physical distance
                brain.update_distance(sensor_dist)

            # --- STEP 3: DECISION (THINKING) ---
            # Pass detections to the brain to decide the next action
            action, speed, steer = brain.decide(detections)

            # --- STEP 4: ACTION (COMMANDING) ---
            # Send the final command package to the car via UDP
            net.send_command(action, speed, steer)

            # --- STEP 5: VISUALIZATION (MONITORING) ---
            # Calculate FPS to ensure GTX 1650 is performing well
            fps = 1 / (time.time() - loop_start_time)
            
            # Draw the current action and FPS on the screen for real-time debugging
            status_text = f"Action: {action} | FPS: {int(fps)}"
            cv2.putText(frame, status_text, (20, 50), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            
            # Display the camera feed with YOLO boxes
            cv2.imshow("Arda's Autonomous Vehicle Control Center", frame)

            # --- STEP 6: EMERGENCY EXIT ---
            # Press 'q' to stop the script safely
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("🛑 User initiated emergency stop.")
                break

    except Exception as e:
        print(f"⚠️ Critical System Error: {e}")

    finally:
        # --- CLEANUP PHASE ---
        # Stop the motors and release camera resources before exiting
        print("🔧 Cleaning up resources and stopping vehicle...")
        net.send_command("SYSTEM_OFF", 0, 0)
        vision.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()