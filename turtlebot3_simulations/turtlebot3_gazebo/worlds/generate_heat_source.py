#!/usr/bin/env python3
import random
import os

# Maze boundaries for random heat source placement
X_MIN, X_MAX = -2.0, 2.0
Y_MIN, Y_MAX = -2.0, 2.0
DISTANCE_THRESHOLD = 0.5  # Min distance between heat sources

# Function to calculate Euclidean distance
def distance(p1, p2):
    return ((p1[0] - p2[0])  2 + (p1[1] - p2[1])  2) ** 0.5

# Generate non-overlapping random positions for heat sources
def generate_positions(count=3):
    positions = []
    while len(positions) < count:
        x = round(random.uniform(X_MIN, X_MAX), 2)
        y = round(random.uniform(Y_MIN, Y_MAX), 2)
        if all(distance((x, y), existing) >= DISTANCE_THRESHOLD for existing in positions):
            positions.append((x, y))
    return positions

# Generate SDF block for a heat source (Red Light + Temperature Sensor)
def generate_heat_source_sdf(x, y, index):
    return f"""
    <model name='heat_source_{index}'>
        <static>true</static>
        <pose>{x} {y} 0 0 0 0</pose>
        <link name='link'>
            <visual name='visual'>
                <geometry>
                    <sphere>
                        <radius>0.2</radius>
                    </sphere>
                </geometry>
                <material>
                    <ambient>1 0 0 1</ambient> <!-- Red color -->
                </material>
            </visual>
            <sensor type="temperature" name="heat_sensor_{index}">
                <always_on>1</always_on>
                <update_rate>10</update_rate>
                <temperature>
                    <ambient>80</ambient>  <!-- Heat source temperature -->
                    <variance>2.0</variance>
                </temperature>
            </sensor>
        </link>
        <light name='heat_source_light_{index}' type='point'>
            <pose>0 0 1 0 0 0</pose>
            <diffuse>1 0 0 1</diffuse>  <!-- Red Light -->
            <specular>0.1 0.1 0.1 1</specular>
            <attenuation>
                <range>5</range>
                <constant>0.5</constant>
                <linear>0.01</linear>
                <quadratic>0.001</quadratic>
            </attenuation>
        </light>
    </model>
    """

# Integrate generated heat sources into the maze world file
def integrate_heat_sources_into_world(world_path, output_path):
    positions = generate_positions()
    heat_blocks = [generate_heat_source_sdf(x, y, i) for i, (x, y) in enumerate(positions)]

    with open(world_path, "r") as file:
        world_data = file.read()

    # Insert heat sources before </world>
    updated_world = world_data.replace("</world>", "\n".join(heat_blocks) + "\n</world>")

    with open(output_path, "w") as file:
        file.write(updated_world)

    print(f" 3 heat sources generated at: {positions}")
    print(f" Updated world saved at: {output_path}")

if name == "main":
    current_dir = os.path.dirname(os.path.abspath(file))
    world_path = os.path.join(current_dir, "../worlds/prim_maze_world.world")
    output_path = os.path.join(current_dir, "../worlds/prim_maze_world_with_heat.world")

    integrate_heat_sources_into_world(world_path, output_path)
