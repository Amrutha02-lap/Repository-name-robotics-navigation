import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
import math


class LidarSimulator(Node):

    def __init__(self):
        super().__init__('lidar_simulator')

        self.publisher_ = self.create_publisher(
            LaserScan,
            '/scan',
            10
        )

        self.timer = self.create_timer(
            0.2,
            self.publish_scan
        )

        self.get_logger().info('LiDAR Simulator started')

    def publish_scan(self):

        scan = LaserScan()

        scan.header.stamp = self.get_clock().now().to_msg()
        scan.header.frame_id = 'laser_frame'

        scan.angle_min = -math.pi / 2
        scan.angle_max = math.pi / 2
        scan.angle_increment = math.pi / 180

        scan.range_min = 0.1
        scan.range_max = 10.0

        # 181 measurements: -90° to +90°
        scan.ranges = [3.0] * 181

        self.publisher_.publish(scan)


def main(args=None):

    rclpy.init(args=args)

    node = LidarSimulator()

    rclpy.spin(node)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()