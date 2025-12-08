#!/usr/bin/env python3
"""
Scan Frame Remapper
(Remapper Frame Scan)

Subscribes to /scan topic and republishes with cleaned frame_id (removes roomba/ prefix).
(Subscribe ke topik /scan dan mempublikasikan ulang dengan frame_id yang dibersihkan (menghapus prefix roomba/))

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
        
        # Subscribe ke scan asli
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan_raw',
            self.scan_callback,
            10
        )
        
        # Publisher untuk scan yang sudah di-remap
        self.scan_pub = self.create_publisher(LaserScan, '/scan', 10)
        
        self.get_logger().info('Scan Frame Remapper ready!')
        
    def scan_callback(self, msg):
        """Remap frame_id dan publikasikan ulang"""
        # Buat pesan baru dengan frame_id yang dibersihkan
        cleaned_msg = LaserScan()
        cleaned_msg.header = msg.header
        
        # Hapus prefix roomba/ dari frame_id
        if msg.header.frame_id.startswith('roomba/'):
            cleaned_msg.header.frame_id = msg.header.frame_id[7:]  # Hapus 'roomba/'
            
        # Salin semua field lainnya
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
