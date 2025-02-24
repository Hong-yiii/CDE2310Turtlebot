turtlebot3_simulations provides the simulation environment for turtlebot3, nothing else.

commands are structured as `ros2 launch turtlebot3_gazebo maze_world.launch.py`
    "bot" followed by "launch file"

#### models: 
    contains the different types of turtlebot, may need to update if significant changes to physical design for collision detection

#### launch: 
    the python scripts that handles the overall of launching, eg. defining starting position, robot, enviroment etc (eg. maze_world.world)
    this might have to be updated as we add sensors etc

#### worlds:
    the physical env files, they end with .world

## Generating random new maze:
    run generate_maze.py while inside worlds folder, it will create a new world that will overwrite maze_world


## Todo: 

- Add heat as a param at points on the map @nathan
- Add ramp on the maze

Hongyi's thughts on the approach: maybe what we can do is segment it, so after the generate maze is ran, we create another function to go and edit maze_world.world to add these extra features