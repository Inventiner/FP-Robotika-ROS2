import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    pkg_sim_name = 'robo_roomba_sim'
    pkg_sim_share = get_package_share_directory(pkg_sim_name)

    map_file_path = os.path.join(pkg_sim_share, 'maps', 'cafe_map_auto.yaml')
    
    nav2_params_path = os.path.join(pkg_sim_share, 'config', 'nav2_params.yaml')

    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_sim_share, 'launch', 'sim_launch.py')
        )
    )

    nav2_bringup = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('nav2_bringup'), 'launch', 'bringup_launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'True',
            'map': map_file_path,
            'params_file': nav2_params_path
        }.items()
    )

    return LaunchDescription([
        sim_launch,
        nav2_bringup,
    ])