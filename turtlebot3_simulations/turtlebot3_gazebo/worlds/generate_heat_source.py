#!/usr/bin/env python3
import random
import os

# Maze boundaries for random light placement
X_MIN, X_MAX = -2.0, 2.0
Y_MIN, Y_MAX = -2.0, 2.0
DISTANCE_THRESHOLD = 0.5  # Min distance between light sources

# Function to calculate Euclidean distance
def distance(p1, p2):
    return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5

# Generate non-overlapping random positions for the heat sources
def generate_positions(count=3):
    positions = []
    while len(positions) < count:
        x = round(random.uniform(X_MIN, X_MAX), 2)
        y = round(random.uniform(Y_MIN, Y_MAX), 2)
        if all(distance((x, y), existing) >= DISTANCE_THRESHOLD for existing in positions):
            positions.append((x, y))
    return positions

# Generate SDF light block for each heat source
def generate_light_sdf(x, y, index):
    return f"""
    <light name='heat_source_light_{index}' type='point'>
      <pose>{x} {y} 1 0 0 0</pose>
      <diffuse>1 0 0 1</diffuse> <!-- Red light -->
      <specular>0.1 0.1 0.1 1</specular>
      <attenuation>
        <range>10</range>
        <constant>0.5</constant>
        <linear>0.01</linear>
        <quadratic>0.001</quadratic>
      </attenuation>
    </light>
    """

# Integrate generated lights into the maze world
def integrate_lights_into_world(world_path, output_path):
    positions = generate_positions()
    light_blocks = [generate_light_sdf(x, y, i) for i, (x, y) in enumerate(positions)]

    with open(world_path, "r") as file:
        world_data = file.read()

    # Insert lights before </world>
    updated_world = world_data.replace("</world>", "\n".join(light_blocks) + "\n</world>")

    with open(output_path, "w") as file:
        file.write(updated_world)

    print(f" 3 heat source lights generated at: {positions}")
    print(f" Updated world saved at: {output_path}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    world_path = os.path.join(current_dir, "../worlds/prim_maze_world.world")
    output_path = os.path.join(current_dir, "../worlds/prim_maze_world_with_heat.world")

    integrate_lights_into_world(world_path, output_path)
