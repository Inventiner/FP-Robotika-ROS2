import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from std_msgs.msg import Bool
import math

class LidarProcessorNode(Node):
    def __init__(self):
        super().__init__('lidar_processor_node')
        
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.lidar_callback,
            10)
            
        self.publisher_ = self.create_publisher(Bool, '/collision_warning', 10)
        
        self.safety_threshold = 0.5
        self.get_logger().info('Lidar Processor Node started. Publishing danger warnings.')

    def lidar_callback(self, msg):
        valid_ranges = [r for r in msg.ranges if not (math.isinf(r) or math.isnan(r) or r == 0.0)]
        if not valid_ranges:
            min_distance = float('inf')
        else:
            min_distance = min(valid_ranges)

        danger_msg = Bool()
        
        if min_distance < self.safety_threshold:
            danger_msg.data = True
        else:
            danger_msg.data = False
            
        self.publisher_.publish(danger_msg)

def main(args=None):
    rclpy.init(args=args)
    lidar_processor_node = LidarProcessorNode()
    rclpy.spin(lidar_processor_node)
    lidar_processor_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()