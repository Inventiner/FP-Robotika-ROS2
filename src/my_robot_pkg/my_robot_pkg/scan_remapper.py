#!/usr/bin/env python3
"""
Scan Frame Remapper

Subscribes to /scan topic and republishes with cleaned frame_id (removes roomba/ prefix).

Author: GitHub Copilot
Date: December 8, 2025
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan


class ScanRemapper(Node):
    
    def __init__(self):
        super().__init__('scan_remapper')
        
        self.get_logger().info('Scan Frame Remapper starting...')
        
        # Subscribe to original scan
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan_raw',
            self.scan_callback,
            10
        )
        
        # Publisher for remapped scan
        self.scan_pub = self.create_publisher(LaserScan, '/scan', 10)
        
        self.get_logger().info('Scan Frame Remapper ready!')
        
    def scan_callback(self, msg):
        """Remap frame_id and republish"""
        # Create new message with cleaned frame_id
        cleaned_msg = LaserScan()
        cleaned_msg.header = msg.header
        
        # Remove roomba/ prefix from frame_id
        if msg.header.frame_id.startswith('roomba/'):
            cleaned_msg.header.frame_id = msg.header.frame_id[7:]  # Remove 'roomba/'
            
        # Copy all other fields
        cleaned_msg.angle_min = msg.angle_min
        cleaned_msg.angle_max = msg.angle_max
        cleaned_msg.angle_increment = msg.angle_increment
        cleaned_msg.time_increment = msg.time_increment
        cleaned_msg.scan_time = msg.scan_time
        cleaned_msg.range_min = msg.range_min
        cleaned_msg.range_max = msg.range_max
        cleaned_msg.ranges = msg.ranges
        cleaned_msg.intensities = msg.intensities
        
        self.scan_pub.publish(cleaned_msg)


def main(args=None):
    rclpy.init(args=args)
    node = ScanRemapper()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
