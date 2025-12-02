import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool
from geometry_msgs.msg import Twist

class RobotDriverNode(Node):
    def __init__(self):
        super().__init__('robot_driver_node')
        
        self.subscription = self.create_subscription(
            Bool,
            '/collision_warning',
            self.collision_callback,
            10)
            
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.get_logger().info('Robot Driver Node started. Awaiting warnings.')

    def collision_callback(self, msg):
        command = Twist()
        
        if msg.data == True:
            self.get_logger().warn('Danger detected! Stopping and turning.')
            command.linear.x = 0.0
            command.angular.z = 0.5
        else:
            self.get_logger().info('Path is clear. Moving forward.')
            command.linear.x = 0.7
            command.angular.z = 0.0
            
        self.publisher_.publish(command)

def main(args=None):
    rclpy.init(args=args)
    robot_driver_node = RobotDriverNode()
    rclpy.spin(robot_driver_node)
    robot_driver_node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()