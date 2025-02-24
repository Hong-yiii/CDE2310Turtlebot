import random

def create_wall(x, y, length, orientation):
    """
    Generate SDF code for a wall placed at (x, y) with a specific length and orientation.
    """
    wall = f"""
    <model name="wall_{x}_{y}">
      <static>true</static>
      <link name="link">
        <collision name="collision">
          <geometry>
            <box>
              <size>{length} 0.5 1</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>{length} 0.5 1</size>
            </box>
          </geometry>
        </visual>
      </link>
      <pose>{x} {y} 0.5 0 0 {orientation}</pose>
    </model>
    """
    return wall

def generate_maze(size=5, min_wall_width=0.5):
    """
    Generate a random maze with enclosing walls and a single entrance.
    """
    maze = []
    # Enclosing walls
    maze.append(create_wall(0, -size/2, size, 0))  # Bottom wall (Entrance)
    maze.append(create_wall(0, size/2, size, 0))   # Top wall
    maze.append(create_wall(-size/2, 0, size, 1.5708))  # Left wall
    maze.append(create_wall(size/2, 0, size, 1.5708))   # Right wall

    # Internal random walls
    for _ in range(15):  # Adjust for complexity
        x = round(random.uniform(-size/2 + 0.5, size/2 - 0.5), 2)
        y = round(random.uniform(-size/2 + 0.5, size/2 - 0.5), 2)
        length = round(random.uniform(0.5, 1.5), 2)
        orientation = random.choice([0, 1.5708])  # 0° or 90°
        maze.append(create_wall(x, y, length, orientation))

    return "\n".join(maze)

def save_maze_to_world():
    maze_walls = generate_maze()

    sdf_content = f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="random_maze_world">

    <!-- Plugins -->
    <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"></plugin>
    <plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"></plugin>
    <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster"></plugin>
    <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors">
      <render_engine>ogre2</render_engine>
    </plugin>
    <plugin filename="gz-sim-imu-system" name="gz::sim::systems::Imu"></plugin>

    <!-- Basic Environment -->
    <include>
      <uri>model://ground_plane</uri>
    </include>
    <include>
      <uri>model://sun</uri>
    </include>

    <!-- Maze Walls -->
    {maze_walls}

    <!-- Camera and GUI Settings -->
    <gui fullscreen="0">
      <camera name="user_camera">
        <pose>0 0 10 0 1.5708 0</pose>
        <view_controller>orbit</view_controller>
      </camera>
    </gui>

    <!-- Physics Configuration -->
    <physics type="ode">
      <real_time_update_rate>1000.0</real_time_update_rate>
      <max_step_size>0.001</max_step_size>
      <real_time_factor>1</real_time_factor>
      <ode>
        <solver>
          <type>quick</type>
          <iters>150</iters>
        </solver>
      </ode>
    </physics>

  </world>
</sdf>
"""
    with open("maze_world.world", "w") as file:
        file.write(sdf_content)
    print("Maze saved to maze_world.world")

# Generate and save the maze
save_maze_to_world()
