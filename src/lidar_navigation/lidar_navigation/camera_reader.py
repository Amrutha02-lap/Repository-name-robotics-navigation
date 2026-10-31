import rclpy
from rclpy.node import Node

from sensor_msgs.msg import Image
from cv_bridge import CvBridge

import cv2


class CameraReader(Node):

    def __init__(self):
        super().__init__('camera_reader')

        self.image_saved = False

        self.bridge = CvBridge()

        self.subscription = self.create_subscription(
            Image,
            '/camera/image_raw',
            self.camera_callback,
            10
        )

        self.get_logger().info('Camera reader started!')

    def camera_callback(self, msg):

        # Convert ROS image into OpenCV image
        frame = self.bridge.imgmsg_to_cv2(
            msg,
            desired_encoding='bgr8'
        )

        # Display the camera image
        cv2.imshow('Robot Camera', frame)

        # Required for OpenCV window to update
        cv2.waitKey(1)

        # Save ONLY the first frame
        if not self.image_saved:
            cv2.imwrite(
                '/home/amrutha/api_learning/robot_camera.jpg',
                frame
            )

            self.image_saved = True

            self.get_logger().info(
                'Saved robot camera image!'
            )


def main(args=None):

    rclpy.init(args=args)

    node = CameraReader()

    try:
        rclpy.spin(node)

    except KeyboardInterrupt:
        pass

    finally:
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()