from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    nav_robot_pkg = FindPackageShare('nav_robot_description')
    nav2_bringup_pkg = FindPackageShare('nav2_bringup')
    slam_pkg = FindPackageShare('slam_toolbox')

    params_file = PathJoinSubstitution([
        nav_robot_pkg, 'config', 'nav2_params.yaml'])

    slam_params = PathJoinSubstitution([
        nav_robot_pkg, 'config', 'slam_params.yaml'])

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([nav_robot_pkg, 'launch', 'gazebo.launch.py'])
        )
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([slam_pkg, 'launch', 'online_async_launch.py'])
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'slam_params_file': slam_params
        }.items()
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([nav2_bringup_pkg, 'launch', 'navigation_launch.py'])
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'params_file': params_file,
            'autostart': 'true'
        }.items()
    )

    return LaunchDescription([gazebo, slam, navigation])
