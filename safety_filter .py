#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import LaserScan
import math


class SafetyFilter(Node):
    def __init__(self):
        super().__init__('safety_filter')

        self.SAFETY_DIST = 0.50
        self.min_front_dist = 10.0

        self.last_cmd = TwistStamped()
        self.last_cmd.header.frame_id = 'base_link'
        self.cmd_received = False

        self.sub_scan = self.create_subscription(
            LaserScan, '/scan', self.scan_callback, 10)

        self.sub_cmd = self.create_subscription(
            TwistStamped, '/desired_cmd_vel', self.cmd_callback, 10)

        self.pub = self.create_publisher(
            TwistStamped, '/diff_drive_controller/cmd_vel', 10)

        self.timer = self.create_timer(0.033, self.timer_callback)

        self.get_logger().info("Safety filter active (0.5 m)")

    def scan_callback(self, msg: LaserScan):
        valid = [r for r in msg.ranges
                 if not math.isnan(r) and 0.01 < r < 30.0]
        if valid:
            self.min_front_dist = min(valid)
        else:
            self.min_front_dist = 10.0

    def cmd_callback(self, msg: TwistStamped):
        self.last_cmd = msg
        self.cmd_received = True

    def timer_callback(self):
        if not self.cmd_received:
            return

        out = TwistStamped()
        out.header.stamp = self.get_clock().now().to_msg()
        out.header.frame_id = 'base_link'

        if self.min_front_dist <= self.SAFETY_DIST and self.last_cmd.twist.linear.x > 0:

            out.twist.linear.x = 0.0
            out.twist.angular.z = self.last_cmd.twist.angular.z

        else:
            out.twist = self.last_cmd.twist

        self.pub.publish(out)


def main():
    rclpy.init()
    node = SafetyFilter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()