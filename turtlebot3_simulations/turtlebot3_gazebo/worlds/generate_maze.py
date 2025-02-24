import random

# ==========================
# Maze Configuration Parameters
# ==========================
CELL_SIZE = 0.5      # Distance between cells
WALL_THICKNESS = 0.1 # Thickness of each wall
WALL_HEIGHT = 1.0    # Height of each wall
GRID_SIZE = 10       # Size of the maze grid (NxN)

# ==========================
# Helper: Convert (row,col) to (x,y) in world coordinates
# ==========================
def cell_center_position(row, col):
    """
    Convert grid indices (row, col) into Gazebo world coordinates (x, y).
    We shift by GRID_SIZE/2 so that the maze is centered around (0,0).
    """
    # Notice that row corresponds to "y" and col corresponds to "x" for many setups,
    # but we can choose whichever orientation we prefer as long as we are consistent.
    x = (col - (GRID_SIZE / 2)) * CELL_SIZE + (CELL_SIZE / 2)
    y = (row - (GRID_SIZE / 2)) * CELL_SIZE + (CELL_SIZE / 2)
    return x, y

# ==========================
# Create a wall SDF snippet
# ==========================
def create_wall(x, y, length, orientation):
    """
    Create an SDF wall with collision enabled at (x, y) with a certain length and orientation.
    orientation in radians: 0 => wall extends in x-dim, 1.5708 => extends in y-dim, etc.
    """
    return f"""
    <model name="wall_{x:.2f}_{y:.2f}">
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
      <pose>{x:.3f} {y:.3f} {WALL_HEIGHT/2} 0 0 {orientation}</pose>
    </model>
    """

# ==========================
# Prim's Maze Generation (Remove Walls)
# ==========================
def generate_prim_maze():
    """
    Generate a maze by removing walls using a typical Prim's approach:
    - Start with all walls present (vertical_walls & horizontal_walls = True).
    - Randomly pick a cell, mark visited.
    - Add its walls to a frontier list.
    - While frontier list not empty, pick a wall that connects visited/unvisited -> remove it, add new cell's walls.
    - Convert the resulting wall structure into SDF snippets.
    - Add outer bounding walls.
    """
    # Track which cells have been visited
    visited = [[False]*GRID_SIZE for _ in range(GRID_SIZE)]

    # For a grid of NxN cells:
    # vertical_walls[r][c] = True means there's a wall between (r,c) and (r,c+1)
    vertical_walls = [[True]*(GRID_SIZE-1) for _ in range(GRID_SIZE)]
    # horizontal_walls[r][c] = True means there's a wall between (r,c) and (r+1,c)
    horizontal_walls = [[True]*GRID_SIZE for _ in range(GRID_SIZE-1)]

    # Helper to get neighbors
    def get_neighbors(r, c):
        """ Return valid neighbor cells of (r,c). """
        offsets = [(-1,0),(1,0),(0,-1),(0,1)]
        for dr, dc in offsets:
            nr, nc = r+dr, c+dc
            if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                yield nr, nc

    # Return the list of "walls" that surround a given cell.
    # Each wall is represented by a tuple: (r1, c1, r2, c2).
    # (r1,c1) is the cell on one side, (r2,c2) is the cell on the other side.
    def cell_walls(r, c):
        walls = []
        for nr, nc in get_neighbors(r,c):
            # If neighbor is directly to the right
            if nr == r and nc == c+1:
                walls.append((r, c, r, c+1))  # vertical
            # left
            elif nr == r and nc == c-1:
                walls.append((r, c-1, r, c))  # vertical
            # down
            elif nr == r+1 and nc == c:
                walls.append((r, c, r+1, c))  # horizontal
            # up
            elif nr == r-1 and nc == c:
                walls.append((r-1, c, r, c))  # horizontal
        return walls

    # Pick a random start cell
    start_r = random.randint(0, GRID_SIZE-1)
    start_c = random.randint(0, GRID_SIZE-1)
    visited[start_r][start_c] = True

    # Frontier "walls" = edges that connect our visited region to unvisited cells
    frontier = []
    frontier.extend(cell_walls(start_r, start_c))

    # Prim's main loop
    while frontier:
        # Randomly pick one wall from frontier
        w = random.choice(frontier)
        frontier.remove(w)

        # Wall is between (r1,c1) and (r2,c2)
        r1, c1, r2, c2 = w

        # If one side is visited and the other is unvisited => remove the wall
        if visited[r1][c1] != visited[r2][c2]:
            # Identify which side is unvisited
            if not visited[r1][c1]:
                r_new, c_new = r1, c1
            else:
                r_new, c_new = r2, c2

            # Mark that cell as visited
            visited[r_new][c_new] = True
            # Add its walls to frontier
            frontier.extend(cell_walls(r_new, c_new))

            # Remove that wall from our data structure
            # If it's horizontal or vertical depends on row vs col
            if r1 == r2:
                # same row, so it's a vertical wall
                # between (r1, c1) and (r1, c1+1) if c2 == c1+1
                c_left = min(c1, c2)
                vertical_walls[r1][c_left] = False
            else:
                # same column, so it's a horizontal wall
                # between (r1, c1) and (r1+1, c1) if r2 == r1+1
                r_top = min(r1, r2)
                horizontal_walls[r_top][c1] = False

    # --------------------------------
    # Convert the wall structures into SDF
    # --------------------------------
    sdf_parts = []

    # 1) Add internal vertical walls
    # vertical_walls[r][c] = True => there's a vertical wall between (r,c) and (r,c+1)
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - 1):
            if vertical_walls[r][c]:
                # The wall runs vertically, so it extends in the y-dim,
                # meaning orientation = 1.5708 (90 deg)
                # The center is halfway between these two cells in x.
                # Let's figure out the (x, y) of that "edge"
                # We'll do "cell_center_position" for cell (r,c) and cell (r,c+1) and average them
                x1, y1 = cell_center_position(r, c)
                x2, y2 = cell_center_position(r, c+1)
                wall_x = (x1 + x2) / 2.0
                wall_y = (y1 + y2) / 2.0

                length = CELL_SIZE  # because it spans from cell c to cell c+1 horizontally
                # orientation: 90 degrees
                orientation = 1.5708
                sdf_parts.append(create_wall(wall_x, wall_y, length, orientation))

    # 2) Add internal horizontal walls
    # horizontal_walls[r][c] = True => there's a horizontal wall between (r,c) and (r+1,c)
    for r in range(GRID_SIZE - 1):
        for c in range(GRID_SIZE):
            if horizontal_walls[r][c]:
                # The wall runs horizontally, so orientation = 0
                x1, y1 = cell_center_position(r, c)
                x2, y2 = cell_center_position(r+1, c)
                wall_x = (x1 + x2) / 2.0
                wall_y = (y1 + y2) / 2.0

                length = CELL_SIZE
                orientation = 0
                sdf_parts.append(create_wall(wall_x, wall_y, length, orientation))

    # --------------------------------
    # Finally, add the four bounding walls (same approach as your old code)
    # --------------------------------
    # Because your total maze width is GRID_SIZE*CELL_SIZE,
    # the outer walls must be placed at +/- (GRID_SIZE/2)*CELL_SIZE
    total_width = GRID_SIZE * CELL_SIZE

    # Bottom wall
    sdf_parts.append(create_wall(
        0, -(GRID_SIZE / 2) * CELL_SIZE,
        total_width, 0
    ))
    # Top wall
    sdf_parts.append(create_wall(
        0, (GRID_SIZE / 2) * CELL_SIZE,
        total_width, 0
    ))
    # Left wall
    sdf_parts.append(create_wall(
        -(GRID_SIZE / 2) * CELL_SIZE, 0,
        total_width, 1.5708
    ))
    # Right wall
    sdf_parts.append(create_wall(
        (GRID_SIZE / 2) * CELL_SIZE, 0,
        total_width, 1.5708
    ))

    # Join all SDF pieces
    return "\n".join(sdf_parts)

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
    print("Maze saved successfully (maze_world.world overwritten).")

# ==========================
# Generate and Save the Maze
# ==========================
if __name__ == "__main__":
    save_maze_to_world()
