import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster

class OdomToTfNode(Node):
    def __init__(self):
        super().__init__('odom_to_tf_converter')
        
        self.get_logger().info('Odometry to TF Converter has been started.')

        self.tf_broadcaster = TransformBroadcaster(self)
        self.subscription = self.create_subscription(
            Odometry,
            '/odom',
            self.odom_callback,
            10)
        self.get_logger().info('Odometry to TF Converter has been started.')

    def odom_callback(self, msg):
        t = TransformStamped()

        # Read message content and assign it to corresponding tf variables
        
        # --- THE FIX ---
        # Use the timestamp from the incoming message itself
        t.header.stamp = msg.header.stamp
        # --- END FIX ---
        
        # Use base frame names without prefix
        t.header.frame_id = 'odom'
        t.child_frame_id = 'base_link'

        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z
        t.transform.rotation = msg.pose.pose.orientation

        self.tf_broadcaster.sendTransform(t)

def main(args=None):
    rclpy.init(args=args)
    node = OdomToTfNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()