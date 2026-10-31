# ROS 2 Mobile Robot Navigation (Gazebo + EKF + AMCL + Nav2)

A 4-wheel differential-drive robot that localises itself on a saved map and drives autonomously to a goal while avoiding obstacles. Everything runs in simulation (Gazebo Classic) and is visualised in RViz.

Full video: [docs/demo.mp4](docs/demo.mp4)

## What it does

- **Custom robot:** 4-wheel car described in URDF (body 0.60 x 0.38 x 0.12 m, 5 kg) with a 2D LiDAR, IMU and camera.
- **Simulated world:** a room with obstacles (`room.world`; `room_divider.world` adds a divider).
- **Mapping (SLAM):** `slam_toolbox` (online async mode) builds a map of the room from the LiDAR while the robot drives (`config/slam_params.yaml`). Saved maps are in `maps/`.
- **Sensor fusion (EKF):** `robot_localization` fuses wheel odometry and the IMU into a smoother pose.
- **Localisation (AMCL):** finds the robot's position on the saved map `room_map`.
- **Navigation (Nav2):** click **Nav2 Goal** in RViz; the robot plans a path and drives there, avoiding obstacles.
- **Obstacle stop:** a Python node (`lidar_reader`) reads the LiDAR and stops the robot when something is closer than 1 m in front.
- **Command bridge:** type `forward` or `back` in a terminal and the robot navigates to a fixed map position through Nav2 (`voice_command_bridge`). Speech input is planned (see To do).
- **Named locations:** `go_to_location.py` sends the robot to a named place such as `start` or `corner`.
- **Autonomous exploration:** `exploration_system.launch.py` uses [m-explore-ros2](https://github.com/robo-friends/m-explore-ros2) (third-party) to explore the room automatically.

## How it works

```
Gazebo (robot + room + obstacles)
   |  /scan (LiDAR), /odom (wheels), /imu
   v
EKF (robot_localization) --> fused odom -> base_link
   |
AMCL + map_server --> map -> odom (robot position on the saved map)
   |
Nav2:  global planner (NavFn)  -->  path
       local planner  (DWB)    -->  /cmd_vel_nav
       costmaps (global + local) built from the map and live LiDAR
       velocity smoother       -->  /cmd_vel  --> robot moves
   |
RViz: map, TF, costmaps, path, 2D Pose Estimate, Nav2 Goal
```

### Startup sequence

`navigation_system.launch.py` starts everything in order, with timers so each part is ready before the next one needs it:

| Time | What starts |
| --- | --- |
| 0 s | Gazebo, robot spawned, robot_state_publisher |
| 3 s | EKF |
| 8 s | Map server + AMCL (localisation) |
| 15 s | Nav2 (planner, controller, behaviours, costmaps) |
| 18 s | RViz |

Wait until RViz shows **Navigation: active** and **Localization: active** before sending a goal.

### Main settings (`config/nav2_params.yaml`)

| Part | Setting |
| --- | --- |
| AMCL | 300 to 1000 particles, likelihood-field laser model, differential motion model, initial pose (0, 0, 0) |
| Global planner | NavFn (Dijkstra), goal tolerance 0.5 m |
| Local planner | DWB, max speed 0.26 m/s, max turn rate 1.0 rad/s, controller at 10 Hz |
| Goal tolerance | 0.25 m position, 0.25 rad heading |
| Global costmap | static map + obstacle layer + inflation (0.65 m radius) |
| Local costmap | 3 x 3 m rolling window, 0.05 m resolution, obstacle layer + inflation |
| Robot footprint | 0.60 x 0.48 m rectangle |
| Recovery behaviours | spin, back up, drive on heading, wait, assisted teleop |
| Velocity smoother | limits speed and acceleration before commands reach the robot |

### EKF (`config/ekf.yaml`)

Runs at 30 Hz in 2D mode. It uses forward velocity from `/odom`, and yaw and yaw rate from the IMU.

## Repository structure

```
.
├── src/
│   ├── nav_robot_description/     # robot, world, Nav2 config and launch files
│   │   ├── config/                # nav2_params.yaml, ekf.yaml, slam_params.yaml
│   │   ├── launch/                # navigation_system, gazebo, exploration_system
│   │   ├── maps/                  # room_map, explored_map
│   │   ├── scripts/               # go_to_location.py
│   │   ├── urdf/                  # nav_robot.urdf
│   │   └── worlds/                # room.world, room_divider.world
│   ├── lidar_navigation/          # Python nodes: obstacle stop, Nav2 command bridge, LiDAR simulator, camera reader
│   └── m-explore-ros2/            # third-party frontier exploration
├── maps/                          # saved maps
├── config_backup/                 # backup of parameter files
└── docs/                          # demo video/GIF, TF tree diagram
```

## Requirements

- Ubuntu 22.04
- ROS 2 **Humble**
- Gazebo **Classic** (gazebo_ros_pkgs)
- Nav2, nav2_bringup, robot_localization, slam_toolbox, RViz2

```bash
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup \
  ros-humble-robot-localization ros-humble-slam-toolbox \
  ros-humble-gazebo-ros-pkgs ros-humble-xacro
```

## Build and run

```bash
# Build
cd ~/robotics_nav/nav_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash

# Launch Gazebo + EKF + AMCL + Nav2 + RViz
ros2 launch nav_robot_description navigation_system.launch.py
```

**In RViz:**
1. Wait about 20 seconds until Navigation and Localization both say **active**.
2. If the robot is not drawn at its real position, click **2D Pose Estimate**, then click and drag on the map to set position and direction.
3. Click **Nav2 Goal**, then click and drag on the map to set the goal. The robot drives there in Gazebo.

The TF tree is in [docs/tf_tree.pdf](docs/tf_tree.pdf).

## Python nodes and scripts

| Command (`ros2 run lidar_navigation ...`) | File | What it does |
| --- | --- | --- |
| `navigation` | `lidar_reader.py` | Reactive obstacle stop. Reads `/scan`, looks at the beam straight ahead, drives forward at 0.2 m/s and stops when the distance is below 1.0 m. Publishes to `/cmd_vel` directly. |
| `voice_command_bridge` | `voice_command_bridge.py` | Command bridge. Waits for Nav2, then takes typed commands (`forward`, `back`, `stop`, `exit`). `forward` goes to map position (2.0, 0.0), `back` to (-2.0, 0.0). Shows distance remaining and the result. |
| `simulator` | `lidar_simulator.py` | LiDAR simulator node. |
| `camera_reader` | `camera_reader.py` | Reads camera images from the robot. |

Another script, outside the package: `nav_robot_description/scripts/go_to_location.py` sends a Nav2 goal to a named location (`start` = (0, 0), `corner` = (2.40, -1.18)). Add more places by editing `LOCATIONS`.

Run these in a new terminal after sourcing the workspace. Use the command bridge and `go_to_location.py` **with Nav2 running**:

```bash
ros2 run lidar_navigation voice_command_bridge
python3 src/nav_robot_description/scripts/go_to_location.py
```

`navigation` (the obstacle stop) is a separate demo. Run it **without Nav2**, because both would publish to `/cmd_vel` and fight each other:

```bash
ros2 run lidar_navigation navigation
```

## Mapping with SLAM

To build a new map, run `slam_toolbox` in mapping mode (`config/slam_params.yaml`), drive the robot around the room, then save the map:

```bash
ros2 run nav2_map_server map_saver_cli -f maps/my_map
```

`exploration_system.launch.py` starts Gazebo, `slam_toolbox` (online async) and Nav2 together, and works with `m-explore-ros2` so the robot can explore by itself. Use SLAM **or** AMCL, not both at once, because both publish the `map -> odom` transform.

## Problems faced

| Problem | Likely cause | Status |
| --- | --- | --- |
| Robot sometimes does not reach the clicked goal, or takes a long, slow path | Wrong initial pose, or tuning of costmap / planner / controller | Improved by parameter changes; not yet fully re-tested |
| RViz messages: "timestamp earlier than all data in the transform cache" | Seen at startup and when simulation runs slower than real time | Monitoring |
| Gazebo real-time factor below 1 (about 0.6 to 0.9) | Laptop is running Gazebo, RViz and Nav2 together | Known limitation |
| RViz GLSL error about samplers | Graphics driver quirk; the map still displays correctly | Ignored |

## Ideas to test next (goal drift)

- [ ] Check that only one node publishes `odom -> base_link` (the EKF **and** the Gazebo plugin both can).
- [ ] Check that only one node publishes to `/cmd_vel` (do not run `lidar_reader` together with Nav2).
- [ ] Reduce the inflation radius (0.65 m is large for this room) and compare paths.
- [ ] Reduce `allow_unknown` / `track_unknown_space` so paths stay in known space.
- [ ] Run 10 goals and record how many are reached.

## To do

- [ ] Re-test the last navigation fix across many goals and record the success rate.
- [ ] Make the obstacle stop safer: check a cone of beams (about 30 degrees) instead of one beam, and treat `nan` / `inf` readings correctly.
- [ ] Test on a real robot.

## Credits

- [Nav2](https://nav2.org), [robot_localization](https://github.com/cra-ros-pkg/robot_localization), [slam_toolbox](https://github.com/SteveMacenski/slam_toolbox)
- [m-explore-ros2](https://github.com/robo-friends/m-explore-ros2) for frontier exploration

## Author

Amrutha, robotics internship project.
