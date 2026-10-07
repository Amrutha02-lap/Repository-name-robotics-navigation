import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist


class LidarReader(Node):

    def __init__(self):
        super().__init__('lidar_reader')

        # Receive LiDAR data
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            10
        )

        # Send movement commands
        self.cmd_pub = self.create_publisher(
            Twist,
            '/cmd_vel',
            10
        )

        self.get_logger().info('LiDAR Reader started')


    def scan_callback(self, msg):

        # Get distance directly in front of robot
        front_distance = msg.ranges[len(msg.ranges) // 2]

        # Create movement command
        cmd = Twist()

        if front_distance < 1.0:

            # Obstacle closer than 1 metre -> STOP
            cmd.linear.x = 0.0
            cmd.angular.z = 0.0

            self.get_logger().warn(
                f'Front distance: {front_distance:.2f} m -> STOP'
            )

        else:

            # Path clear -> MOVE FORWARD
            cmd.linear.x = 0.2
            cmd.angular.z = 0.0

            self.get_logger().info(
                f'Front distance: {front_distance:.2f} m -> MOVE'
            )

        # Publish movement command
        self.cmd_pub.publish(cmd)


def main(args=None):

    rclpy.init(args=args)

    node = LidarReader()

    rclpy.spin(node)

    node.destroy_node()

    rclpy.shutdown()


if __name__ == '__main__':
    main()