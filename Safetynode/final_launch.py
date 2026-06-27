from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution, EnvironmentVariable
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    # ===== TurtleBot3 Navigation2 launch 포함 =====
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([
                FindPackageShare('turtlebot3_navigation2'),
                'launch',
                'navigation2.launch.py'
            ])
        ),
        launch_arguments={
            # SLAM으로 생성한 최종 지도 사용
            'map': PathJoinSubstitution([
                EnvironmentVariable('HOME'),
                'setros_map_new.yaml'
            ]),

            # 속도, 가속도, costmap 등이 튜닝된 Nav2 파라미터 파일
            'params_file': PathJoinSubstitution([
                EnvironmentVariable('HOME'),
                'setros_nav2_params.yaml'
            ]),

            # Nav2 lifecycle 자동 활성화
            'autostart': 'true',
        }.items()
    )

    # ===== 갑툭튀 장애물 Emergency Stop safety node =====
    safety_node = Node(
        package='setros_safety',
        executable='safety_cmd_vel_node',
        name='setros_safety_node',
        output='screen',
        parameters=[{
            # 정면 ±25도 감시
            'front_angle_deg': 25.0,

            # 28cm 이내 장애물 감지 시 정지
            'stop_distance': 0.28,

            # 장애물 제거 후 1초 대기 후 재출발
            'resume_delay': 1.0,
        }]
    )

    return LaunchDescription([
        nav2_launch,
        safety_node,
    ])
