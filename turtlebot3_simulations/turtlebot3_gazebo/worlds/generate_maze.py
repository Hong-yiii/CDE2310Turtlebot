import random

# ==========================
# Maze Configuration Parameters
# ==========================
CELL_SIZE = 0.5      # Distance between cells
WALL_THICKNESS = 0.1 # Thickness of each wall
WALL_HEIGHT = 1.0    # Height of each wall
STEP_SIZE = 1        # Neighbor step size
GRID_SIZE = 10       # Size of the maze grid (NxN)

# ==========================
# Wall Creation Function
# ==========================
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
              <size>{length} {WALL_THICKNESS} {WALL_HEIGHT}</size>
            </box>
          </geometry>
        </collision>
        <visual name="visual">
          <geometry>
            <box>
              <size>{length} {WALL_THICKNESS} {WALL_HEIGHT}</size>
            </box>
          </geometry>
        </visual>
      </link>
      <pose>{x} {y} {WALL_HEIGHT / 2} 0 0 {orientation}</pose>
    </model>
    """
    return wall

# ==========================
# Maze Generation with Prim's Algorithm
# ==========================
def generate_prim_maze():
    """
    Generate a maze using Prim's algorithm with adjustable step size.
    """
    maze = []
    visited = [[False for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

    def neighbors(x, y):
        directions = [(-STEP_SIZE, 0), (STEP_SIZE, 0), (0, -STEP_SIZE), (0, STEP_SIZE)]
        result = []
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
                result.append((nx, ny))
        return result

    # Initialize maze with walls
    wall_list = []
    start_x, start_y = random.randint(0, GRID_SIZE - 1), random.randint(0, GRID_SIZE - 1)
    visited[start_x][start_y] = True
    wall_list.extend(neighbors(start_x, start_y))

    while wall_list:
        wx, wy = random.choice(wall_list)
        wall_list.remove((wx, wy))

        adjacent_cells = [(wx + dx, wy + dy) for dx, dy in [(-STEP_SIZE, 0), (STEP_SIZE, 0), (0, -STEP_SIZE), (0, STEP_SIZE)] if 0 <= wx + dx < GRID_SIZE and 0 <= wy + dy < GRID_SIZE]
        unvisited_neighbors = [cell for cell in adjacent_cells if not visited[cell[0]][cell[1]]]

        if len(unvisited_neighbors) == 1:
            nx, ny = unvisited_neighbors[0]
            visited[nx][ny] = True

            # Convert grid coordinates to actual positions
            x_center = (wx - GRID_SIZE // 2) * CELL_SIZE
            y_center = (wy - GRID_SIZE // 2) * CELL_SIZE

            # Wall between the two cells
            orientation = 0 if wx == nx else 1.5708  # Horizontal or vertical
            length = CELL_SIZE
            maze.append(create_wall(x_center, y_center, length, orientation))

            # Add new neighbors to the wall list
            wall_list.extend(neighbors(nx, ny))

    # Add outer walls
    maze.append(create_wall(0, -(GRID_SIZE / 2) * CELL_SIZE, GRID_SIZE * CELL_SIZE, 0))  # Bottom
    maze.append(create_wall(0, (GRID_SIZE / 2) * CELL_SIZE, GRID_SIZE * CELL_SIZE, 0))   # Top
    maze.append(create_wall(-(GRID_SIZE / 2) * CELL_SIZE, 0, GRID_SIZE * CELL_SIZE, 1.5708))  # Left
    maze.append(create_wall((GRID_SIZE / 2) * CELL_SIZE, 0, GRID_SIZE * CELL_SIZE, 1.5708))   # Right

    return "\n".join(maze)

# ==========================
# Saving Maze to Gazebo World
# ==========================
def save_maze_to_world():
    maze_walls = generate_prim_maze()

    sdf_content = f"""<?xml version="1.0" ?>
<sdf version="1.6">
  <world name="prim_maze_world">

    <!-- Plugins -->
    <plugin filename="gz-sim-physics-system" name="gz::sim::systems::Physics"/>
    <plugin filename="gz-sim-user-commands-system" name="gz::sim::systems::UserCommands"/>
    <plugin filename="gz-sim-scene-broadcaster-system" name="gz::sim::systems::SceneBroadcaster"/>
    <plugin filename="gz-sim-sensors-system" name="gz::sim::systems::Sensors">
      <render_engine>ogre2</render_engine>
    </plugin>
    <plugin filename="gz-sim-imu-system" name="gz::sim::systems::Imu"/>

    <!-- Basic Environment (Fuel URIs) -->
    <include>
      <uri>https://fuel.gazebosim.org/1.0/OpenRobotics/models/Ground Plane</uri>
    </include>
    <include>
      <uri>https://fuel.gazebosim.org/1.0/OpenRobotics/models/Sun</uri>
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
    with open("maze_world.world", "w") as file:
        file.write(sdf_content)
    print("maze_world.world saved successfully! Old maze_world.world will be overwritten.")

# ==========================
# Generate and Save the Maze
# ==========================
save_maze_to_world()
