import sys
import rclpy
from rclpy.executors import ExternalShutdownException
from rclpy.node import Node
import struct
from std_msgs.msg import String

from can_plugins2.msg import Frame


speed = 1
can_id = 0x160
mode = 5

def frame_get_logger_pub(node_class, frame):
    node_class.get_logger().info(f'Publish: id= {frame.id}, data= {frame.data}, dlc= {frame.dlc}')

def byteslist_of_float(n):
    bytes_n = struct.pack('>d', n)
    bytes_list = [0] * 8
    for i in range(8):
        bytes_list[i] = int(bytes_n[i])
    return bytes_list


class TestControl(Node):
    def mode_pub(self, can_id, mode):
        self.pub = self.create_publisher(Frame, 'can_tx', 10)
        self.can_id = can_id
        frame = Frame()
        frame.id = int(self.can_id)
        frame.data = [mode, 0, 0, 0, 0, 0, 0, 0]
        frame.dlc = int(1)
        self.pub.publish(frame)
        frame_get_logger_pub(self, frame)

    def speed_control_pub(self, speed):
        #NodeClass内で使用する.
        #速度(speed rad/s)で回す. 
        frame = Frame()
        frame.id = int(self.can_id + 1)
        frame.dlc = int(4)
        frame.data = byteslist_of_float(speed)
        self.pub.publish(frame)
        frame_get_logger_pub(self, frame)


    def __init__(self):
        super().__init__('motor_node')
        self.i = 0

        self.mode_pub(can_id, mode)
        self.timer = self.create_timer(1, self.timer_callback)


    def timer_callback(self):
        ispeed = speed + speed * (self.i % 2)
        self.speed_control_pub(ispeed)
        self.i += 1
    


def main():
    rclpy.init()
    node = TestControl()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    except ExternalShutdownException:
        sys.exit(1)
    finally:
        node.destroy_node()
        rclpy.try_shutdown()