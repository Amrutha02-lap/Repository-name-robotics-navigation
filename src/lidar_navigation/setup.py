from setuptools import find_packages, setup

package_name = 'lidar_navigation'

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
    maintainer='amrutha',
    maintainer_email='amruthasprasad01@gmail.com',
    description='TODO: Package description',
    license='TODO: License declaration',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'navigation = lidar_navigation.lidar_reader:main',
            'simulator = lidar_navigation.lidar_simulator:main',
            'voice_command_bridge = lidar_navigation.voice_command_bridge:main',
        ],
    },
)
