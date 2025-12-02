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
            LaserScan, 
            '/scan', 
            self.lidar_callback, 
            QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT))

        self.regions = {'front': float('inf'), 'left': float('inf')}
        self.state_description = ''
        
        # Timer: Run the logic 10 times a second
        self.timer = self.create_timer(0.1, self.control_loop)
        self.get_logger().info("Mode: SEEK & WALL FOLLOW (Left Hug)")

    def lidar_callback(self, msg):
        ranges = msg.ranges
        size = len(ranges)
        
        # Helper to clean data
        def get_min(start, end):
            # Scan slice
            data = ranges[start:end]
            # Filter valid ranges (0.0 to 10.0m)
            valid = [x for x in data if 0.0 < x < 10.0]
            return min(valid) if valid else 10.0

        # Front: Narrow slice (-15 to +15 degrees)
        # Gazebo 360 array: 0 is front. 
        self.regions['front'] = min(get_min(0, 15), get_min(size-15, size))
        
        # Left: Slice from 45 to 100 degrees (The side we hug)
        left_start = int(size * (45/360))
        left_end = int(size * (100/360))
        self.regions['left'] = get_min(left_start, left_end)

    def control_loop(self):
        msg = Twist()
        
        # --- SENSOR DATA ---
        front_dist = self.regions['front']
        left_dist = self.regions['left']
        
        # --- CONSTANTS ---
        STOP_DIST = 0.8     # When to stop before hitting wall
        WALL_DIST = 0.6     # Ideal distance from wall
        SPEED = 0.4         # Forward speed
        TURN_SPEED = 0.6    # Rotation speed
        
        # --- LOGIC ---
        
        # 1. OBSTACLE AHEAD (Collision Avoidance)
        if front_dist < STOP_DIST:
            self.state_description = "HIT WALL -> Turning Right"
            msg.linear.x = 0.0
            msg.angular.z = -TURN_SPEED # Turn Right to align wall to our Left
            
        # 2. FOUND WALL ON LEFT (Wall Following Logic)
        elif left_dist < 1.2:
            self.state_description = "FOLLOWING WALL (Left)"
            msg.linear.x = SPEED
            
            # Simple P-Controller for steering
            # If left_dist is LARGE (too far) -> error is positive -> Turn Left (+)
            # If left_dist is SMALL (too close) -> error is negative -> Turn Right (-)
            error = left_dist - WALL_DIST
            
            # Clamp the turning so it doesn't wobble crazily
            rotation = error * 1.5 
            msg.angular.z = max(min(rotation, 0.6), -0.6)
            
            self.state_description += f" [Dist: {left_dist:.2f}m]"

        # 3. NO WALLS (Seek Mode)
        else:
            self.state_description = "SEEKING (Driving Straight)"
            msg.linear.x = SPEED
            msg.angular.z = 0.0 # Just go straight

        # --- DEBUG ---
        print(f"Front: {front_dist:.2f}m | Left: {left_dist:.2f}m | Action: {self.state_description}")
        self.publisher_.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = SmartVacuum()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()