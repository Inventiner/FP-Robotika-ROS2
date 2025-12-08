#!/usr/bin/env python3
"""
TF Prefix Remover Node
(Node Penghapus Prefix TF)

This node subscribes to /tf and /tf_static, removes the 'roomba/' prefix from all frame names,
and republishes them. This is necessary because Gazebo automatically adds the model name
as a prefix to all frames, but Nav2 expects frames without prefixes.
(Node ini berlangganan ke /tf dan /tf_static, menghapus prefix 'roomba/' dari semua nama frame,
dan mempublikasikannya kembali. Ini diperlukan karena Gazebo secara otomatis menambahkan nama model
sebagai prefix ke semua frame, tapi Nav2 mengharapkan frame tanpa prefix.)

Author: GitHub Copilot
Date: December 8, 2025
"""

import rclpy
from rclpy.node import Node
from tf2_msgs.msg import TFMessage
import copy


class TFPrefixRemover(Node):
    """Removes 'roomba/' prefix from all TF frame names"""
    # (Menghapus prefix 'roomba/' dari semua nama frame TF)
    
    PREFIX_TO_REMOVE = 'roomba/'
    
    def __init__(self):
        super().__init__('tf_prefix_remover')
        
        self.get_logger().info('TF Prefix Remover node starting...')
        self.get_logger().info(f'Will remove prefix: "{self.PREFIX_TO_REMOVE}" from all TF frames')
        
        # Subscribe to Gazebo's TF topic (with roomba/ prefix in frame names)
        # (Subscribe ke topik TF Gazebo (dengan prefix roomba/ pada nama frame))
        self.tf_sub = self.create_subscription(
            TFMessage,
            '/model/roomba/tf',
            self.tf_callback,
            100  # Large queue for TF
        )
        
        self.tf_static_sub = self.create_subscription(
            TFMessage,
            '/tf_static',
            self.tf_static_callback,
            100  # Large queue for static TF
        )
        
        # Publishers for cleaned TF topics (without prefix)
        # (Publisher untuk topik TF yang sudah dibersihkan (tanpa prefix))
        self.tf_pub = self.create_publisher(TFMessage, '/tf', 100)
        self.tf_static_pub = self.create_publisher(TFMessage, '/tf_static', 100)
        
        self.get_logger().info('TF Prefix Remover node ready!')
        
        # Track what we've cleaned (for logging)
        # (Lacak apa yang sudah kita bersihkan untuk logging)
        self.cleaned_frames = set()
        
    def remove_prefix(self, frame_name):
        """Remove the roomba/ prefix from a frame name if it exists"""
        # (Hapus prefix roomba/ dari nama frame jika ada)
        if frame_name.startswith(self.PREFIX_TO_REMOVE):
            cleaned = frame_name[len(self.PREFIX_TO_REMOVE):]
            
            # Log first time we clean a frame
            # (Log saat pertama kali kita membersihkan frame)
            if frame_name not in self.cleaned_frames:
                self.cleaned_frames.add(frame_name)
                self.get_logger().info(f'Cleaning frame: "{frame_name}" -> "{cleaned}"')
            
            return cleaned
        return frame_name
    
    def clean_transform(self, transform):
        """Create a copy of transform with cleaned frame names"""
        # (Buat salinan transform dengan nama frame yang dibersihkan)
        cleaned = copy.deepcopy(transform)
        cleaned.header.frame_id = self.remove_prefix(transform.header.frame_id)
        cleaned.child_frame_id = self.remove_prefix(transform.child_frame_id)
        return cleaned
    
    def tf_callback(self, msg):
        """Process dynamic TF transforms"""
        # (Proses transformasi TF dinamis)
        # Debug: Log frame names in received message
        # (Debug: Log nama frame pada pesan yang diterima)
        if not hasattr(self, '_logged_frames'):
            for transform in msg.transforms:
                self.get_logger().info(f'Received transform: {transform.header.frame_id} -> {transform.child_frame_id}')
            self._logged_frames = True
        
        # Create new message with cleaned frame names
        # (Buat pesan baru dengan nama frame yang dibersihkan)
        cleaned_msg = TFMessage()
        
        for transform in msg.transforms:
            cleaned_transform = self.clean_transform(transform)
            
            # Only republish if we actually cleaned something
            # (avoid republishing frames that were already clean)
            # (Hanya publikasikan ulang jika kita benar-benar membersihkan sesuatu)
            # (hindari mempublikasikan ulang frame yang sudah bersih)
            if (cleaned_transform.header.frame_id != transform.header.frame_id or
                cleaned_transform.child_frame_id != transform.child_frame_id):
                cleaned_msg.transforms.append(cleaned_transform)
        
        # Publish if we have any cleaned transforms
        # (Publikasikan jika kita memiliki transform yang dibersihkan)
        if cleaned_msg.transforms:
            self.tf_pub.publish(cleaned_msg)
    
    def tf_static_callback(self, msg):
        """Process static TF transforms"""
        # (Proses transformasi TF statis)
        # Create new message with cleaned frame names
        # (Buat pesan baru dengan nama frame yang dibersihkan)
        cleaned_msg = TFMessage()
        
        for transform in msg.transforms:
            cleaned_transform = self.clean_transform(transform)
            
            # Only republish if we actually cleaned something
            # (Hanya publikasikan ulang jika ada perubahan)
            if (cleaned_transform.header.frame_id != transform.header.frame_id or
                cleaned_transform.child_frame_id != transform.child_frame_id):
                cleaned_msg.transforms.append(cleaned_transform)
        
        # Publish if we have any cleaned transforms
        # (Publikasikan jika ada transform yang dibersihkan)
        if cleaned_msg.transforms:
            self.tf_static_pub.publish(cleaned_msg)


def main(args=None):
    rclpy.init(args=args)
    node = TFPrefixRemover()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
