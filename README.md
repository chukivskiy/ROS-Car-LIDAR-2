## Safety Filter Node

A lightweight safety node for differential drive robots that filters velocity commands to prevent forward collisions using LiDAR data.

This node acts as a middleware between your teleoperation node (publishing to `/desired_cmd_vel`) and the robot controller (subscribing to `/diff_drive_controller/cmd_vel`).

### Features

- Allows full control over **rotation** (`angular.z`) and **backward motion** (`linear.x < 0`) at all times
- Blocks **forward motion** (`linear.x > 0`) when any obstacle is closer than **0.5 m** in front
- Uses data from the standard `/scan` topic (`sensor_msgs/msg/LaserScan`)
- Very low latency (~30 Hz update rate)
- Ignores invalid/NaN range values
- Simple and robust — no complex sector logic or dynamic tuning (yet)

### How It Works

1. Subscribes to `/desired_cmd_vel` (TwistStamped) — raw teleop commands
2. Subscribes to `/scan` — reads the minimum valid range across **all** laser beams
3. If `min_distance ≤ 0.50 m` **and** the desired `linear.x > 0` → sets `linear.x = 0.0`
4. Publishes filtered command to `/diff_drive_controller/cmd_vel`

Backward movement and in-place turning are **never** blocked.


```bash
# 1. Launch simulation
ros2 launch my_diff_robot robot.launch.py

# 2. Run teleoperation node (publishes /desired_cmd_vel (change publish topic from /diff_drive_controller/cmd_vel to /desired_cmd_vel manualy) 
python3 src/my_diff_robot/scripts/simple_teleop.py 

# 3. Run the safety filter
python3 src/my_diff_robot/scripts/safety_filter.py 
Now press w / arrow up → robot stops in front of obstacles closer than 50 cm, but can still turn (a/d) and go backward (x / s).
