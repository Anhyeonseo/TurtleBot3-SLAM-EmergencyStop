import math
import time

import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data

from geometry_msgs.msg import TwistStamped
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String


class SafetyCmdVelNode(Node):
    def __init__(self):
        super().__init__('setros_safety_node')

        # ===== Safety parameters =====
        # front_angle_deg: 로봇 정면 기준 감시 각도 범위
        # stop_distance: 이 거리 안에 장애물이 들어오면 정지
        # resume_delay: 장애물 제거 후 재출발 전 대기 시간
        self.declare_parameter('front_angle_deg', 25.0)
        self.declare_parameter('stop_distance', 0.28)
        self.declare_parameter('resume_delay', 1.0)

        self.front_angle_deg = float(self.get_parameter('front_angle_deg').value)
        self.stop_distance = float(self.get_parameter('stop_distance').value)
        self.resume_delay = float(self.get_parameter('resume_delay').value)

        # ===== Internal state =====
        self.latest_cmd = TwistStamped()
        self.obstacle_detected = False
        self.last_obstacle_time = 0.0
        self.state = 'NORMAL'

        # 디버깅용: 마지막 전방 최소 거리/각도 저장
        self.last_min_front_distance = float('inf')
        self.last_min_front_angle = 0.0

        # ===== Subscribers =====
        # Nav2 controller_server가 만든 원본 속도 명령
        self.cmd_sub = self.create_subscription(
            TwistStamped,
            '/cmd_vel_nav',
            self.cmd_callback,
            10
        )

        # LiDAR scan 구독
        # TurtleBot3 /scan은 sensor-data QoS를 사용하므로 qos_profile_sensor_data 필요
        self.scan_sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.scan_callback,
            qos_profile_sensor_data
        )

        # ===== Publishers =====
        # TurtleBot3가 실제로 구독하는 최종 속도 명령
        self.cmd_pub = self.create_publisher(
            TwistStamped,
            '/cmd_vel',
            10
        )

        # safety 상태 확인용 토픽
        self.state_pub = self.create_publisher(
            String,
            '/safety_state',
            10
        )

        # 20Hz로 최종 /cmd_vel 출력
        self.timer = self.create_timer(0.05, self.timer_callback)

        self.get_logger().info('setros_safety_node started')
        self.get_logger().info(f'front_angle_deg={self.front_angle_deg}')
        self.get_logger().info(f'stop_distance={self.stop_distance}')
        self.get_logger().info(f'resume_delay={self.resume_delay}')

    def cmd_callback(self, msg):
        # Nav2가 만든 최신 속도 명령 저장
        self.latest_cmd = msg

    def normalize_angle_deg(self, angle_deg):
        # LiDAR 각도를 -180 ~ +180도 범위로 정규화
        # /scan이 0~360도 형식으로 들어와도 전방 판단 가능
        return ((angle_deg + 180.0) % 360.0) - 180.0

    def scan_callback(self, msg):
        front_ranges = []

        for i, r in enumerate(msg.ranges):
            # 유효하지 않은 거리값 제거
            if math.isinf(r) or math.isnan(r):
                continue

            if r < msg.range_min or r > msg.range_max:
                continue

            # 현재 scan index의 각도 계산
            angle_rad = msg.angle_min + i * msg.angle_increment
            angle_deg = math.degrees(angle_rad)
            angle_deg = self.normalize_angle_deg(angle_deg)

            # 정면 ±front_angle_deg 범위만 감시
            if abs(angle_deg) <= self.front_angle_deg:
                front_ranges.append((angle_deg, r))

        if not front_ranges:
            self.obstacle_detected = False
            self.last_min_front_distance = float('inf')
            self.last_min_front_angle = 0.0
            return

        # 전방 영역에서 가장 가까운 장애물 추출
        min_angle, min_distance = min(front_ranges, key=lambda x: x[1])

        self.last_min_front_distance = min_distance
        self.last_min_front_angle = min_angle

        # 정지 거리 안에 들어오면 갑툭튀 장애물로 판단
        if min_distance < self.stop_distance:
            self.obstacle_detected = True
            self.last_obstacle_time = time.time()
        else:
            self.obstacle_detected = False

    def make_stop_cmd(self):
        # 모든 선속도/각속도를 0으로 만드는 정지 명령 생성
        stop = TwistStamped()
        stop.header.stamp = self.get_clock().now().to_msg()
        stop.header.frame_id = self.latest_cmd.header.frame_id

        stop.twist.linear.x = 0.0
        stop.twist.linear.y = 0.0
        stop.twist.linear.z = 0.0

        stop.twist.angular.x = 0.0
        stop.twist.angular.y = 0.0
        stop.twist.angular.z = 0.0

        return stop

    def timer_callback(self):
        now = time.time()

        # 1. 갑툭튀 장애물 감지 → 즉시 정지
        if self.obstacle_detected:
            self.state = 'SUDDEN_OBSTACLE_STOP'
            out_cmd = self.make_stop_cmd()

        # 2. 장애물 제거 직후 → 일정 시간 대기
        elif now - self.last_obstacle_time < self.resume_delay:
            self.state = 'WAIT_AFTER_SUDDEN_STOP'
            out_cmd = self.make_stop_cmd()

        # 3. 평상시 → Nav2 속도 명령 그대로 전달
        else:
            self.state = 'NORMAL'
            out_cmd = self.latest_cmd

        # 최종 속도 명령 publish
        out_cmd.header.stamp = self.get_clock().now().to_msg()
        self.cmd_pub.publish(out_cmd)

        # 현재 safety 상태 publish
        state_msg = String()
        state_msg.data = self.state
        self.state_pub.publish(state_msg)


def main(args=None):
    rclpy.init(args=args)

    node = SafetyCmdVelNode()

    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
