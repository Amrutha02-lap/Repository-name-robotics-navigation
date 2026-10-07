import math
import rclpy

from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import (
    BasicNavigator,
    TaskResult
)


class VoiceCommandBridge(Node):

    def __init__(self):
        super().__init__('voice_command_bridge')

        self.navigator = BasicNavigator()

        self.get_logger().info('Waiting for Nav2 to become active...')
        self.navigator.waitUntilNav2Active()
        self.get_logger().info('Nav2 is ready. Enter a command.')

    def create_goal(self, x, y, yaw=0.0):
        goal_pose = PoseStamped()

        goal_pose.header.frame_id = 'map'
        goal_pose.header.stamp = self.navigator.get_clock().now().to_msg()

        goal_pose.pose.position.x = x
        goal_pose.pose.position.y = y
        goal_pose.pose.position.z = 0.0

        # Convert yaw angle to quaternion
        goal_pose.pose.orientation.z = math.sin(yaw / 2.0)
        goal_pose.pose.orientation.w = math.cos(yaw / 2.0)

        return goal_pose

    def send_goal(self, command):
        if command == 'forward':
            # This is an absolute map coordinate
            goal = self.create_goal(
                x=2.0,
                y=0.0,
                yaw=0.0
            )

        elif command == 'back':
            # This is also an absolute map coordinate
            goal = self.create_goal(
                x=-2.0,
                y=0.0,
                yaw=math.pi
            )

        else:
            self.get_logger().warn(
                "Unknown command. Use: forward, back, stop, or exit"
            )
            return

        self.get_logger().info(f'Sending {command} goal to Nav2...')
        self.navigator.goToPose(goal)

        while not self.navigator.isTaskComplete():
            feedback = self.navigator.getFeedback()

            if feedback is not None:
                distance = feedback.distance_remaining
                self.get_logger().info(
                    f'Distance remaining: {distance:.2f} m',
                    throttle_duration_sec=2.0
                )

        result = self.navigator.getResult()

        if result == TaskResult.SUCCEEDED:
            self.get_logger().info('Goal reached successfully.')

        elif result == TaskResult.CANCELED:
            self.get_logger().warn('Navigation task canceled.')

        elif result == TaskResult.FAILED:
            self.get_logger().error('Navigation task failed.')

        else:
            self.get_logger().warn('Navigation finished with an unknown result.')

    def stop_robot(self):
        if not self.navigator.isTaskComplete():
            self.get_logger().info('Canceling current navigation task...')
            self.navigator.cancelTask()
        else:
            self.get_logger().info('No active navigation task.')


def main(args=None):
    rclpy.init(args=args)

    node = VoiceCommandBridge()

    try:
        while rclpy.ok():
            command = input(
                '\nEnter command '
                '(forward / back / stop / exit): '
            ).strip().lower()

            if command == 'exit':
                node.stop_robot()
                break

            elif command == 'stop':
                node.stop_robot()

            elif command in ['forward', 'back']:
                node.send_goal(command)

            else:
                print('Unknown command. Try forward, back, stop, or exit.')

    except KeyboardInterrupt:
        node.get_logger().info('Keyboard interrupt received.')
        node.stop_robot()

    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
