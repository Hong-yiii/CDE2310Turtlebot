import random

def create_wall(x, y, length, orientation):
    """
    Create an SDF wall with collision enabled at (x, y) with a certain length and orientation.
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

def generate_prim_maze(grid_size=10, cell_size=0.5):
    """
    Generate a maze using Prim's algorithm.
    """
    maze = []
    visited = [[False for _ in range(grid_size)] for _ in range(grid_size)]

    def neighbors(x, y):
        directions = [(-2, 0), (2, 0), (0, -2), (0, 2)]
        result = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < grid_size and 0 <= ny < grid_size:
                result.append((nx, ny))
        return result

    # Initialize maze with walls
    wall_list = []
    start_x, start_y = random.randint(0, grid_size - 1), random.randint(0, grid_size - 1)
    visited[start_x][start_y] = True
    wall_list.extend(neighbors(start_x, start_y))

    while wall_list:
        wx, wy = random.choice(wall_list)
        wall_list.remove((wx, wy))

        adjacent_cells = [(wx + dx, wy + dy) for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2)] if 0 <= wx + dx < grid_size and 0 <= wy + dy < grid_size]
        unvisited_neighbors = [cell for cell in adjacent_cells if not visited[cell[0]][cell[1]]]

        if len(unvisited_neighbors) == 1:
            nx, ny = unvisited_neighbors[0]
            visited[nx][ny] = True

            # Convert grid coordinates to actual positions
            x_center = (wx - grid_size // 2) * cell_size
            y_center = (wy - grid_size // 2) * cell_size

            # Wall between the two cells
            orientation = 0 if wx == nx else 1.5708  # Horizontal or vertical
            length = cell_size
            maze.append(create_wall(x_center, y_center, length, orientation))

            # Add new neighbors to the wall list
            wall_list.extend(neighbors(nx, ny))

    # Add outer walls
    maze.append(create_wall(0, -(grid_size / 2) * cell_size, grid_size * cell_size, 0))  # Bottom
    maze.append(create_wall(0, (grid_size / 2) * cell_size, grid_size * cell_size, 0))   # Top
    maze.append(create_wall(-(grid_size / 2) * cell_size, 0, grid_size * cell_size, 1.5708))  # Left
    maze.append(create_wall((grid_size / 2) * cell_size, 0, grid_size * cell_size, 1.5708))   # Right

    return "\n".join(maze)

def save_maze_to_world():
    maze_walls = generate_prim_maze()

    sdf_content = f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="prim_maze_world">

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

    <!-- Camera Configuration -->
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
    </physics>

  </world>
</sdf>
"""
    with open("prim_maze.world", "w") as file:
        file.write(sdf_content)
    print("Maze saved to prim_maze.world")

# Generate and save the maze
save_maze_to_world()
