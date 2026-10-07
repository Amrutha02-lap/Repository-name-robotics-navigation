import rclpy
from rclpy.action import ActionClient
from rclpy.node import Node
from nav2_msgs.action import NavigateToPose
from geometry_msgs.msg import PoseStamped

LOCATIONS = {
    "start": (0.0, 0.0),
    "corner": (2.40, -1.18),
}


class GoToLocation(Node):
    def __init__(self):
        super().__init__('go_to_location')
        self.client = ActionClient(self, NavigateToPose, 'navigate_to_pose')

    def send_goal(self, x, y):
        self.get_logger().info('Waiting for Nav2 action server...')
        self.client.wait_for_server()

        goal = NavigateToPose.Goal()
        goal.pose = PoseStamped()
        goal.pose.header.frame_id = 'map'
        goal.pose.header.stamp = self.get_clock().now().to_msg()
        goal.pose.pose.position.x = x
        goal.pose.pose.position.y = y
        goal.pose.pose.orientation.w = 1.0

        self.get_logger().info(f'Sending goal: x={x}, y={y}')
        future = self.client.send_goal_async(goal)
        rclpy.spin_until_future_complete(self, future)
        goal_handle = future.result()

        if not goal_handle.accepted:
            self.get_logger().info('Goal rejected')
            return

        self.get_logger().info('Goal accepted, driving...')
        result_future = goal_handle.get_result_async()
        rclpy.spin_until_future_complete(self, result_future)
        status = result_future.result().status
        if status == 4:
            self.get_logger().info('Reached the goal!')
        else:
            self.get_logger().info(f'Did not reach the goal (status={status}).')


def main():
    rclpy.init()
    node = GoToLocation()

    print("Available locations:", ", ".join(LOCATIONS.keys()))
    while True:
        name = input("Type a location name (or 'quit'): ").strip().lower()
        if name == 'quit':
            break
        if name not in LOCATIONS:
            print("Unknown location. Try:", ", ".join(LOCATIONS.keys()))
            continue
        x, y = LOCATIONS[name]
        node.send_goal(x, y)

    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
