#!/usr/bin/env python3
"""
TF Alias Helper Node

This node subscribes to TF topics and applies aliasing rules to frame names.
It can remove prefixes (e.g. 'roomba/base_link' -> 'base_link') or add them.

Author: GitHub Copilot
Date: December 8, 2025
"""

import rclpy
from rclpy.node import Node
from tf2_msgs.msg import TFMessage
import copy

class TFAliasHelper(Node):
    def __init__(self):
        super().__init__('tf_alias_helper')
        
        self.declare_parameter('mode', 'remove_prefix') # 'remove_prefix' or 'add_prefix'
        self.declare_parameter('prefix', 'roomba/')
        self.declare_parameter('input_topic_tf', '/tf_in')
        self.declare_parameter('input_topic_tf_static', '/tf_static_in')
        
        self.mode = self.get_parameter('mode').value
        self.prefix = self.get_parameter('prefix').value
        input_tf = self.get_parameter('input_topic_tf').value
        input_tf_static = self.get_parameter('input_topic_tf_static').value
        
        self.get_logger().info(f'TF Alias Helper starting. Mode: {self.mode}, Prefix: {self.prefix}')
        
        self.tf_sub = self.create_subscription(
            TFMessage,
            input_tf,
            self.tf_callback,
            100
        )
        
        self.tf_static_sub = self.create_subscription(
            TFMessage,
            input_tf_static,
            self.tf_static_callback,
            100
        )
        
        self.tf_pub = self.create_publisher(TFMessage, '/tf', 100)
        self.tf_static_pub = self.create_publisher(TFMessage, '/tf_static', 100)
        
        self.cleaned_frames = set()

    def process_frame(self, frame_name):
        if self.mode == 'remove_prefix':
            if frame_name.startswith(self.prefix):
                return frame_name[len(self.prefix):]
        elif self.mode == 'add_prefix':
            if not frame_name.startswith(self.prefix):
                return self.prefix + frame_name
        return frame_name

    def process_msg(self, msg):
        new_msg = TFMessage()
        for transform in msg.transforms:
            new_transform = copy.deepcopy(transform)
            new_transform.header.frame_id = self.process_frame(transform.header.frame_id)
            new_transform.child_frame_id = self.process_frame(transform.child_frame_id)
            new_msg.transforms.append(new_transform)
            
            # Logging
            key = (transform.header.frame_id, new_transform.header.frame_id)
            if key not in self.cleaned_frames:
                self.cleaned_frames.add(key)
                self.get_logger().info(f'Mapping: "{transform.header.frame_id}" -> "{new_transform.header.frame_id}"')
                
        return new_msg

    def tf_callback(self, msg):
        new_msg = self.process_msg(msg)
        if new_msg.transforms:
            self.tf_pub.publish(new_msg)

    def tf_static_callback(self, msg):
        new_msg = self.process_msg(msg)
        if new_msg.transforms:
            self.tf_static_pub.publish(new_msg)

def main(args=None):
    rclpy.init(args=args)
    node = TFAliasHelper()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
