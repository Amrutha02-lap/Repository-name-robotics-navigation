from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    TimerAction
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node


def generate_launch_description():

    nav_robot_pkg = FindPackageShare('nav_robot_description')
    nav2_bringup_pkg = FindPackageShare('nav2_bringup')

    # Map file
    map_file = PathJoinSubstitution([
        nav_robot_pkg,
        'maps',
        'room_map.yaml'
    ])

    # Nav2 parameters
    params_file = PathJoinSubstitution([
        nav_robot_pkg,
        'config',
        'nav2_params.yaml'
    ])

    # EKF parameters
    ekf_params = PathJoinSubstitution([
        nav_robot_pkg,
        'config',
        'ekf.yaml'
    ])

    # Gazebo simulation
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                nav_robot_pkg,
                'launch',
                'gazebo.launch.py'
            ])
        )
    )

    # Extended Kalman Filter
    ekf_node = Node(
        package='robot_localization',
        executable='ekf_node',
        name='ekf_filter_node',
        output='screen',
        parameters=[
            ekf_params,
            {'use_sim_time': True}
        ]
    )

    # AMCL localization and map server
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

    # Nav2 navigation
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

    # RViz
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=[
            '-d',
            PathJoinSubstitution([
                nav2_bringup_pkg,
                'rviz',
                'nav2_default_view.rviz'
            ])
        ],
        parameters=[
            {'use_sim_time': True}
        ],
        output='screen'
    )

    # Startup sequence
    start_ekf = TimerAction(
        period=3.0,
        actions=[ekf_node]
    )

    start_localization = TimerAction(
        period=8.0,
        actions=[localization]
    )

    start_navigation = TimerAction(
        period=15.0,
        actions=[navigation]
    )

    start_rviz = TimerAction(
        period=18.0,
        actions=[rviz_node]
    )

    return LaunchDescription([
        gazebo,
        start_ekf,
        start_localization,
        start_navigation,
        start_rviz
    ])