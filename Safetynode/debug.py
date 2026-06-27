python3-<< 'EOF'
import rclpy, math
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan

class ScanAngleFinder(Node):
    def __init__(self):
        super().__init__('scan_angle_finder')

        # /scan은 sensor-data QoS로 구독해야 안정적으로 수신됨
        self.sub = self.create_subscription(
            LaserScan,
            '/scan',
            self.cb,
            qos_profile_sensor_data
        )

    def norm(self, deg):
        # 0~360도 또는 -180~180도 형식을 -180~180도로 통일
        return ((deg + 180.0) % 360.0) - 180.0

    def cb(self, msg):
        vals = []

        for i, r in enumerate(msg.ranges):
            if math.isinf(r) or math.isnan(r):
                continue
            if r < msg.range_min or r > msg.range_max:
                continue

            raw_deg = math.degrees(msg.angle_min + i * msg.angle_increment)
            norm_deg = self.norm(raw_deg)
            vals.append((r, raw_deg, norm_deg))

        # 가장 가까운 scan point 10개 출력
        vals.sort(key=lambda x: x[0])

        print("=== closest 10 scan points ===")
        for r, raw, norm in vals[:10]:
            print(f"distance={r:.3f} m | raw_angle={raw:.1f} deg | normalized_angle={norm:.1f} deg")

        rclpy.shutdown()

rclpy.init()
node = ScanAngleFinder()
rclpy.spin(node)
EOF
