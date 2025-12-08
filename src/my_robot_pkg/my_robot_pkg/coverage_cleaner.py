import rclpy
from rclpy.node import Node
from nav2_simple_commander.robot_navigator import BasicNavigator
from geometry_msgs.msg import PoseStamped
import tf_transformations
import time
import math
from rclpy.duration import Duration

# --- Fungsi Pembantu untuk Membuat Waypoints ---
def generate_cleaning_waypoints(logger=None):
    waypoints = []
    # Batas peta: X: -5.04 sampai 17.41, Y: -6.16 sampai 3.34
    # Area pembersihan yang aman dengan margin
    # Disesuaikan agar lebih aman dari tembok 
    Y_START = -5.0  # Sebelumnya -5.5
    Y_END = 2.5     # Sebelumnya 3.0
    X_LEFT = -3.5   # Sebelumnya -4.0
    X_RIGHT = 3.0   # Sebelumnya 3.5
    LANE_WIDTH = 0.5  # Jarak antar jalur yang sedikit lebih lebar untuk keandalan 
    
    if logger:
        logger.info(f"[DEBUG] Waypoint Generation Config:")
        logger.info(f"  Y_START: {Y_START}, Y_END: {Y_END}")
        logger.info(f"  X_LEFT: {X_LEFT}, X_RIGHT: {X_RIGHT}")
        logger.info(f"  LANE_WIDTH: {LANE_WIDTH}")

    y = Y_START
    direction = 1 
    row_count = 0
    
    # Lacak yaw sebelumnya untuk memastikan transisi yang mulus di awal baris
    # Yaw awal adalah 0.0 (asumsi robot mulai menghadap kanan atau netral)
    prev_yaw = 0.0

    while y <= Y_END:
        row_count += 1
        
        # 1. Tentukan arah dan yaw untuk AKHIR baris
        if direction == 1:
            start_x = X_LEFT
            end_x = X_RIGHT
            curr_yaw = 0.0
        else:
            start_x = X_RIGHT
            end_x = X_LEFT
            curr_yaw = math.pi
        
        # Buat quaternion untuk orientasi
        q_start = tf_transformations.quaternion_from_euler(0, 0, prev_yaw)
        q_end = tf_transformations.quaternion_from_euler(0, 0, curr_yaw)

        # 2. Tentukan titik MULAI (Pose 1)
        # Gunakan prev_yaw agar robot tiba di awal baris sesuai orientasi akhir baris sebelumnya
        pose_start = PoseStamped()
        pose_start.header.frame_id = 'map'
        pose_start.header.stamp.sec = 0
        pose_start.pose.position.x = start_x
        pose_start.pose.position.y = y
        pose_start.pose.orientation.x = q_start[0]
        pose_start.pose.orientation.y = q_start[1]
        pose_start.pose.orientation.z = q_start[2]
        pose_start.pose.orientation.w = q_start[3]
        
        # 3. Tentukan titik AKHIR (Pose 2)
        # Gunakan curr_yaw agar robot melintasi baris dengan arah yang benar
        pose_end = PoseStamped()
        pose_end.header.frame_id = 'map'
        pose_end.header.stamp.sec = 0
        pose_end.pose.position.x = end_x
        pose_end.pose.position.y = y
        pose_end.pose.orientation.x = q_end[0]
        pose_end.pose.orientation.y = q_end[1]
        pose_end.pose.orientation.z = q_end[2]
        pose_end.pose.orientation.w = q_end[3]
        
        waypoints.append(pose_start)
        waypoints.append(pose_end)
        
        if logger and row_count <= 3:
            logger.info(f"[DEBUG] Row {row_count}: y={y:.2f}, direction={'RIGHT' if direction==1 else 'LEFT'}")
            logger.info(f"  Start: ({start_x:.2f}, {y:.2f}) Yaw: {prev_yaw:.2f}")
            logger.info(f"  End:   ({end_x:.2f}, {y:.2f}) Yaw: {curr_yaw:.2f}")
        
        # 4. Siapkan untuk loop berikutnya
        y += LANE_WIDTH
        direction *= -1
        prev_yaw = curr_yaw # Awal baris berikutnya harus cocok dengan akhir baris ini
    
    if logger:
        y_values = [w.pose.position.y for w in waypoints]
        logger.info(f"[DEBUG] Generated {len(waypoints)} waypoints, Y range: [{min(y_values):.2f}, {max(y_values):.2f}]")
            
    return waypoints

class CoverageCleaner(Node):
    def __init__(self):
        super().__init__('coverage_cleaner')
        self.get_logger().info("=" * 60)
        self.get_logger().info("Coverage Cleaner Node has been started.")
        self.get_logger().info("=" * 60)
        
        # Kita asumsikan stack navigasi sudah berjalan, tapi beri jeda kecil
        # untuk memastikan bridge /clock aktif.
        self.get_logger().info("[DEBUG] Waiting 1 second for system initialization...")
        time.sleep(1.0)
        
        self.get_logger().info("[DEBUG] Creating BasicNavigator instance...")
        self.navigator = BasicNavigator()

        # 1. Atur Pose Awal (DIBUTUHKAN untuk lokalisasi)
        self.get_logger().info("[DEBUG] Setting initial pose at (0.0, 0.0)...")
        initial_pose = PoseStamped()
        initial_pose.header.frame_id = 'map'
        initial_pose.header.stamp = self.navigator.get_clock().now().to_msg()
        initial_pose.pose.position.x = 0.0
        initial_pose.pose.position.y = 0.0
        q = tf_transformations.quaternion_from_euler(0, 0, 0) 
        initial_pose.pose.orientation.x = q[0]
        initial_pose.pose.orientation.y = q[1]
        initial_pose.pose.orientation.z = q[2]
        initial_pose.pose.orientation.w = q[3]
        
        self.navigator.setInitialPose(initial_pose)
        self.get_logger().info("[DEBUG] Initial pose set. Waiting for Nav2 stack activation...")
        
        # 2. Tunggu Nav2 aktif (biasanya beberapa detik setelah pose awal diatur)
        self.get_logger().info("[DEBUG] Calling waitUntilNav2Active()...")
        self.navigator.waitUntilNav2Active()
        self.get_logger().info("=" * 60)
        self.get_logger().info("Nav2 is ACTIVE! Starting coverage mission.")
        self.get_logger().info("=" * 60)

        # 3. Hasilkan dan Kirim Tujuan Pembersihan
        self.start_cleaning_mission()

    def start_cleaning_mission(self):
        
        # Hasilkan Waypoints Zig-Zag
        self.get_logger().info("[DEBUG] Generating waypoints...")
        waypoints = generate_cleaning_waypoints(logger=self.get_logger())
        
        if not waypoints:
            self.get_logger().error("[ERROR] No cleaning waypoints generated.")
            rclpy.shutdown()
            return
        
        # Masukkan posisi robot saat ini sebagai waypoint pertama untuk memastikan awal yang mulus
        self.get_logger().info("[DEBUG] Adding current position as first waypoint...")
        current_pose = PoseStamped()
        current_pose.header.frame_id = 'map'
        current_pose.header.stamp.sec = 0
        current_pose.pose.position.x = 0.0
        current_pose.pose.position.y = 0.0
        q = tf_transformations.quaternion_from_euler(0, 0, 0)
        current_pose.pose.orientation.x = q[0]
        current_pose.pose.orientation.y = q[1]
        current_pose.pose.orientation.z = q[2]
        current_pose.pose.orientation.w = q[3]
        
        # Add current position as first waypoint
        waypoints.insert(0, current_pose)
        
        self.get_logger().info("=" * 60)    
        self.get_logger().info(f"Total waypoints: {len(waypoints)} (including start position)")
        self.get_logger().info("=" * 60)
        
        # Log first few and last few waypoints for debugging
        self.get_logger().info("[DEBUG] First 5 waypoints:")
        for idx, wp in enumerate(waypoints[:5]):
            self.get_logger().info(f"  [{idx}] ({wp.pose.position.x:.2f}, {wp.pose.position.y:.2f})")
        
        self.get_logger().info("[DEBUG] Last 3 waypoints:")
        for idx, wp in enumerate(waypoints[-3:], len(waypoints)-3):
            self.get_logger().info(f"  [{idx}] ({wp.pose.position.x:.2f}, {wp.pose.position.y:.2f})")
        
        # Kirim urutan tujuan ke Nav2
        self.get_logger().info("=" * 60)
        self.get_logger().info("[DEBUG] Sending waypoints to Nav2 via goThroughPoses()...")
        self.get_logger().info("=" * 60)
        
        # Opsional: Berputar untuk membersihkan costmap sebelum mulai
        self.get_logger().info("[DEBUG] Spinning to clear local costmap...")
        self.navigator.spin(spin_dist=1.57) # 90 derajat
        while not self.navigator.isTaskComplete():
            pass
        self.get_logger().info("[DEBUG] Spin complete.")

        self.navigator.goThroughPoses(waypoints)
        
        # --- Loop Pemantauan Misi ---
        self.get_logger().info("[DEBUG] Entering mission monitoring loop...")
        i = 0
        while not self.navigator.isTaskComplete():
            i += 1
            feedback = self.navigator.getFeedback()
            
            if feedback and i % 10 == 0: # Cetak setiap ~1 detik
                self.get_logger().info(f'[PROGRESS] Distance remaining: {feedback.distance_remaining:.2f} meters')
                # Debug pose saat ini jika tersedia di feedback
                if hasattr(feedback, 'current_pose'):
                    p = feedback.current_pose.pose.position
                    self.get_logger().info(f'[DEBUG] Current Pose: ({p.x:.2f}, {p.y:.2f})')
            
            if i % 50 == 0:  # Setiap 5 detik
                self.get_logger().info(f"[DEBUG] Still navigating... (iteration {i})")

            # Opsional: Tambahkan logika pemutus loop untuk pembersihan (misal: cek baterai)
            time.sleep(0.1)  # Jeda kecil untuk mencegah penggunaan CPU berlebih
        
        self.get_logger().info("[DEBUG] Mission monitoring loop completed.")
        self.get_logger().info("=" * 60)
            
        # --- Cek Penyelesaian Misi ---
        result = self.navigator.getResult()
        result_str = str(result)
        
        self.get_logger().info(f"[DEBUG] Raw result: {result}")
        self.get_logger().info(f"[DEBUG] Result string: {result_str}")
        
        if 'SUCCEEDED' in result_str:
            self.get_logger().info("=" * 60)
            self.get_logger().info('*** Cleaning Mission SUCCEEDED! ***')
            self.get_logger().info("=" * 60)
        else:
            self.get_logger().error("=" * 60)
            self.get_logger().error(f'*** Cleaning Mission FAILED with status: {result_str} ***')
            self.get_logger().error("=" * 60)

        # Shutdown the node
        self.get_logger().info("[DEBUG] Shutting down ROS...")
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    try:
        print("[MAIN] Starting Coverage Cleaner...")
        node = CoverageCleaner()
        print("[MAIN] Node created successfully.")
        # Note: We don't need rclpy.spin here as the navigator monitor loop handles waiting.
    except KeyboardInterrupt:
        print("[MAIN] Keyboard interrupt received, shutting down...")
        rclpy.shutdown()
    except Exception as e:
        print(f"[MAIN] ERROR during execution: {e}")
        import traceback
        traceback.print_exc()
        rclpy.shutdown()

if __name__ == '__main__':
    main()