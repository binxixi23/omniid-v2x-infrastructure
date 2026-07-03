import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import json

class OmniIDReceiverNode(Node):
    def __init__(self):
        super().__init__('omniid_receiver_node')
        self.subscription = self.create_subscription(
            String, '/v2x/digital_identity', self.listener_callback, 10
        )
        self.publisher_ = self.create_publisher(String, '/internal/active_identities', 10)
        self.get_logger().info('📻 Bộ thu tín hiệu OmniID trên Robot đã sẵn sàng...')

    def listener_callback(self, msg):
        try:
            data = json.loads(msg.data)
            self.get_logger().info(f"📥 [Bộ thu V2X] Nhận được mã: {data['entity_id']} ({data['sub_class']})")
            # Chuyển tiếp dữ liệu sạch vào bộ xử lý trung tâm
            self.publisher_.publish(msg)
        except Exception as e:
            self.get_logger().error(f"Lỗi phân tích cú pháp dữ liệu: {e}")

def main(args=None):
    rclpy.init(args=args)
    node = OmniIDReceiverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
