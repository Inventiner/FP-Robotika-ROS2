import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from sensor_msgs.msg import LaserScan
from nav_msgs.msg import Odometry
from ros_gz_interfaces.msg import Contacts
from rclpy.qos import ReliabilityPolicy, QoSProfile
import math

class AutonomousMapper(Node):
    def __init__(self):
        super().__init__('autonomous_mapper')
        
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        # Subscribe ke topic LaserScan dan bumper
        # (Berlangganan ke topik LaserScan dan bumper)
        self.create_subscription(LaserScan, '/scan', self.lidar_callback, QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT))
        self.create_subscription(Contacts, '/bumper', self.bumper_callback, 10)

        self.lidar_received = False
        # Data sensor untuk menyimpan jarak yang terukur
        self.sensor_data = {'front': 99.0, 'right_90': 99.0, 'right_45': 99.0}
        
        # State untuk bumper dan pemulihan (recovery)
        self.bumper_hit = False; self.recovery_timer = 0; self.is_recovering = False

        # --- PERSISTENT STATE ---
        # State awal robot
        self.current_state = "SEEKING"
        
        self.kp_dist = 2.0; self.kp_theta = 4.0

        self.get_logger().info("AUTONOMOUS MAPPER 28.0 | Persistent State Machine")
        self.timer = self.create_timer(0.05, self.control_loop) # 20Hz

    def bumper_callback(self, msg):
        # Callback jika bumper menabrak sesuatu
        if len(msg.contacts) > 0 and not self.is_recovering:
            self.bumper_hit = True; self.is_recovering = True
            self.get_logger().warn(">>> BUMPER HIT! <<<")

    def lidar_callback(self, msg):
        # Callback untuk memproses data LIDAR
        self.lidar_received = True; ranges = msg.ranges; size = len(ranges); mid_idx = size // 2
        def get_avg(start, end):
            # Menghitung rata-rata jarak pada range tertentu
            s = ranges[start:end]; v = [r for r in s if 0.1 < r < 10.0]; return sum(v)/len(v) if v else 99.0
        self.sensor_data['front'] = get_avg(mid_idx-15, mid_idx+15)
        r90_idx = int(size * 0.25); self.sensor_data['right_90'] = get_avg(r90_idx-10, r90_idx+10)
        r45_idx = int(size * 0.375); self.sensor_data['right_45'] = get_avg(r45_idx-10, r45_idx+10)

    def control_loop(self):
        cmd_msg = Twist()
        if not self.lidar_received: return

        if self.bumper_hit: self.recovery_timer = 30; self.bumper_hit = False
        # Logika pemulihan jika menabrak
        if self.recovery_timer > 0:
            self.current_state = "RECOVERING"
            if self.recovery_timer > 15: cmd_msg.linear.x = -0.15 # Mundur
            else: cmd_msg.angular.z = 0.7 # Putar
            self.recovery_timer -= 1
            if self.recovery_timer == 0: self.is_recovering = False; self.current_state="SEEKING" # Setelah pulih, cari tembok lagi
            self.publisher_.publish(cmd_msg); return

        front = self.sensor_data['front']; right_90 = self.sensor_data['right_90']
        right_45 = self.sensor_data['right_45']
        
        LINEAR_SPEED = 0.25; TURN_SPEED = 0.6
        INNER_CORNER_STOP_DIST = 0.4; WALL_ACQUIRE_DIST = 0.8
        TARGET_WALL_DIST = 0.35
        
        # ==========================================================
        # PERSISTENT STATE MACHINE
        # ==========================================================
        
        # --- State Actions & Transitions ---
        
        if self.current_state == "SEEKING":
            # Mencari tembok
            cmd_msg.linear.x = LINEAR_SPEED
            # Transisi: Menemukan tembok, mulai berputar
            if front < INNER_CORNER_STOP_DIST or right_90 < WALL_ACQUIRE_DIST:
                self.current_state = "TURNING_INNER"
        
        elif self.current_state == "TURNING_INNER":
            # Berputar di pojok dalam
            cmd_msg.linear.x = 0.0; cmd_msg.angular.z = TURN_SPEED
            # Transisi: Jika depan sudah kosong, mulai ikuti tembok
            if front > INNER_CORNER_STOP_DIST + 0.1:
                self.current_state = "FOLLOW_WALL"
        
        elif self.current_state == "TURNING_OUTER":
            # Berputar di pojok luar
            cmd_msg.linear.x = 0.1; cmd_msg.angular.z = -0.7
            # Transisi: Jika melihat tembok di kanan lagi, mulai ikuti tembok
            if right_90 < WALL_ACQUIRE_DIST:
                self.current_state = "FOLLOW_WALL"

        elif self.current_state == "SIMPLE_FOLLOW":
            # Mode mengikuti tembok sederhana (Proportional Control)
            error = TARGET_WALL_DIST - right_90
            turn = self.kp_dist * error
            cmd_msg.angular.z = max(min(turn, 0.4), -0.4)
            cmd_msg.linear.x = LINEAR_SPEED * 0.7
            # Transisi: Kembali ke mode pintar jika ada kejadian besar
            if front < INNER_CORNER_STOP_DIST: self.current_state = "TURNING_INNER"
            elif right_90 > WALL_ACQUIRE_DIST: self.current_state = "TURNING_OUTER"

        elif self.current_state == "FOLLOW_WALL":
            # Transition Checks (Highest Priority)
            if front < INNER_CORNER_STOP_DIST: self.current_state = "TURNING_INNER"; return
            if right_90 > WALL_ACQUIRE_DIST: self.current_state = "TURNING_OUTER"; return

            # Aksi: Kontrol Proportional-Heading
            ideal_45 = right_90 / 0.707
            heading_error = ideal_45 - right_45
            
            # KUNCI: Jika error heading besar, pindah ke mode sederhana (DUMB)
            if abs(heading_error) > 0.8:
                self.current_state = "SIMPLE_FOLLOW"
                return # Bertindak pada siklus berikutnya
            
            # Jika sensor dapat dipercaya, lakukan kontrol Proportional
            distance_error = TARGET_WALL_DIST - right_90
            turn = (self.kp_dist * distance_error) + (self.kp_theta * heading_error)
            turn = max(min(turn, 1.0), -1.0)
            
            cmd_msg.angular.z = turn
            speed_factor = 1.0 - (abs(turn) * 0.8)
            cmd_msg.linear.x = max(LINEAR_SPEED * speed_factor, 0.05)

        self.publisher_.publish(cmd_msg)
        log_msg = (f"State: {self.current_state:<15} | R90:{right_90:.2f} | CMD: [L:{cmd_msg.linear.x:.2f}, A:{cmd_msg.angular.z:.2f}]")
        self.get_logger().info(log_msg, throttle_duration_sec=0.5)

def main(args=None):
    rclpy.init(args=args); node = AutonomousMapper(); rclpy.spin(node)
    node.destroy_node(); rclpy.shutdown()

if __name__ == '__main__':
    main()