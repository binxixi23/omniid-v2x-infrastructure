import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json
import math

class OmniIDVisionFusionNode(Node):
    def __init__(self):
        super().__init__('omniid_vision_fusion_node')
        
        # Subscribe dữ liệu từ Camera và Hệ thống thu phát V2X
        self.yolo_sub = self.create_subscription(String, '/camera/yolo_detections', self.yolo_callback, 10)
        self.v2x_sub = self.create_subscription(String, '/internal/active_identities', self.v2x_callback, 10)
        
        self.active_digital_identities = {}

    def v2x_callback(self, msg):
        data = json.loads(msg.data)
        self.active_digital_identities[data["entity_id"]] = data

    def yolo_callback(self, msg):
        # Giả lập dữ liệu YOLO quét được: Thấy một cái hộp ở góc 180 độ
        yolo_data = json.loads(msg.data) 
        detected_class = yolo_data["detected_class"]
        camera_angle = yolo_data["bearing_angle"]

        self.get_logger().info(f"👁️ [YOLO Vision] Phát hiện thô: '{detected_class}' tại góc {camera_angle}°")

        # Thuật toán đối chiếu (Matching Logic) để xác thực
        for entity_id, identity in self.active_digital_identities.items():
            v2x_angle = identity["telemetry"]["heading"]
            
            # Nếu góc camera trùng với hướng phát sóng số (sai số cho phép 5 độ)
            if math.isclose(camera_angle, v2x_angle, abs_tol=5.0):
                self.get_logger().warn(
                    f"🎯 [XÁC THỰC THÀNH CÔNG] Vật thể trực quan chính là: '{entity_id}'!\n"
                    f"   ↳ Kích thước thật từ hệ thống số: {identity['dimensions']}\n"
                    f"   ↳ Cơ chế an toàn kích hoạt: {identity['safety_policy']}"
                )
                return

        self.get_logger().info("⚠️ Cảnh báo: Vật thể lạ không có mã định danh số!")

def main(args=None):
    rclpy.init(args=args)
    node = OmniIDVisionFusionNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
