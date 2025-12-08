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
            'cleaning_node = my_robot_pkg.cleaning_node:main',
            'coverage_cleaner = my_robot_pkg.coverage_cleaner:main',
            'odom_to_tf = my_robot_pkg.odom_to_tf:main',
            'tf_prefix_remover = my_robot_pkg.tf_prefix_remover:main',
            'scan_remapper = my_robot_pkg.scan_remapper:main',
            'tf_alias_helper = my_robot_pkg.tf_alias_helper:main',
        ],
    },
)
