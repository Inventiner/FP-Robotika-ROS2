import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from rclpy.qos import ReliabilityPolicy, QoSProfile

class SmartVacuum(Node):
    def __init__(self):
        super().__init__('smart_vacuum')
        
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.subscriber = self.create_subscription(
            LaserScan, '/scan', self.lidar_callback, 
            QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT))

        self.regions = {'front': 99.0, 'left': 99.0}
        self.lidar_received = False
        self.current_state = "SEEKING"
        
        # --- PID CONTROLLER VARIABLES ---
        self.last_error = 0.0
        self.integral = 0.0
        # More "punitive" gains
        self.kp = 4.0  # Stronger reaction to current error
        self.kd = 8.0  # Stronger damping to prevent overshoot
        self.ki = 0.05 # Small integral term to correct persistent drift

        self.get_logger().info("SMART VACUUM INITIALIZED | PID Controller")
        self.timer = self.create_timer(0.1, self.control_loop)

    def lidar_callback(self, msg):
        # ... (this is the same) ...
        self.lidar_received = True; ranges = msg.ranges; size = len(ranges)
        def get_min_in_slice(start, end):
            valid = [r for r in ranges[start:end] if 0.1 < r < 10.0]
            return min(valid) if valid else 99.0
        front_index = size // 2
        self.regions['front'] = get_min_in_slice(front_index - 15, front_index + 15)
        left_index = (size * 3) // 4
        self.regions['left'] = get_min_in_slice(left_index - 20, left_index + 20)

    def control_loop(self):
        cmd_msg = Twist()
        if not self.lidar_received: return

        front_dist = self.regions['front']; left_dist = self.regions['left']
        
        STOP_DIST = 0.4
        WALL_DIST = 0.35 # Tighter 35cm target distance
        SPEED = 0.3
        TURN_SPEED = 0.6
        WALL_FOLLOW_THRESHOLD = 0.8 # Use your tighter threshold

        # --- State Logic ---
        if front_dist < STOP_DIST: self.current_state = "TURNING"
        elif left_dist < WALL_FOLLOW_THRESHOLD: self.current_state = "FOLLOWING"
        elif self.current_state == "FOLLOWING" and left_dist >= WALL_FOLLOW_THRESHOLD: self.current_state = "CORNERING"
        else:
            if self.current_state != "CORNERING": self.current_state = "SEEKING"

        # --- Action based on State ---
        if self.current_state == "TURNING":
            cmd_msg.linear.x = 0.0; cmd_msg.angular.z = -TURN_SPEED
            self.last_error = 0; self.integral = 0 # Reset PID
        
        elif self.current_state == "FOLLOWING":
            cmd_msg.linear.x = SPEED
            
            # --- FULL PID CONTROLLER ---
            error = left_dist - WALL_DIST
            self.integral += error
            derivative = error - self.last_error
            
            turn_adjustment = (self.kp * error) + (self.ki * self.integral) + (self.kd * derivative)
            self.last_error = error
            
            cmd_msg.angular.z = max(min(turn_adjustment, 0.8), -0.8)
            
        elif self.current_state == "CORNERING":
            cmd_msg.linear.x = 0.0; cmd_msg.angular.z = 0.7
            self.last_error = 0; self.integral = 0
            
        elif self.current_state == "SEEKING":
            cmd_msg.linear.x = SPEED; cmd_msg.angular.z = 0.0
            self.last_error = 0; self.integral = 0

        # --- DEBUG ---
        log_msg = (f"State: {self.current_state} | Sensors: [F:{front_dist:.2f}, L:{left_dist:.2f}] | CMD: [L:{cmd_msg.linear.x:.2f}, A:{cmd_msg.angular.z:.2f}]")
        self.get_logger().info(log_msg, throttle_duration_sec=0.5)
        
        self.publisher_.publish(cmd_msg)

def main(args=None):
    rclpy.init(args=args); node = SmartVacuum(); rclpy.spin(node)
    node.destroy_node(); rclpy.shutdown()

if __name__ == '__main__':
    main()