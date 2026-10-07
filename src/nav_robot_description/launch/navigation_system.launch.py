from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node

def generate_launch_description():

    nav_robot_pkg = FindPackageShare('nav_robot_description')
    nav2_bringup_pkg = FindPackageShare('nav2_bringup')

    map_file = PathJoinSubstitution([
        nav_robot_pkg,
        'maps',
        'room_map.yaml'
    ])

    params_file = PathJoinSubstitution([
        nav_robot_pkg,
        'config',
        'nav2_params.yaml'
    ])
    ekf_params = PathJoinSubstitution([
        nav_robot_pkg, 'config', 'ekf.yaml'])

    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[ekf_params]
    )
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                nav_robot_pkg,
                'launch',
                'gazebo.launch.py'
            ])
        )
    )

    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                nav2_bringup_pkg,
                'launch',
                'localization_launch.py'
            ])
        ),
        launch_arguments={
            'map': map_file,
            'use_sim_time': 'true',
            'params_file': params_file,
            'autostart': 'true'
        }.items()
    )

    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                nav2_bringup_pkg,
                'launch',
                'navigation_launch.py'
            ])
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'params_file': params_file,
            'autostart': 'true'
        }.items()
    )

    return LaunchDescription([
        gazebo,
        localization,
        navigation,
	ekf_node
    ])

