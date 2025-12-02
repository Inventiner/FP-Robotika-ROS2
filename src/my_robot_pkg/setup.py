from setuptools import find_packages, setup

package_name = 'my_robot_pkg'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='bithan',
    maintainer_email='bithan@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'robot_driver_node = my_robot_pkg.robot_driver_node:main',
            'lidar_processor_node = my_robot_pkg.lidar_processor_node:main',
            'cleaning_node = my_robot_pkg.cleaning_node:main',
        ],
    },
)
