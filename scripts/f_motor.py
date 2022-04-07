#!/usr/bin/env python
import rospy
from std_msgs.msg import String

def callback(data):
    rospy.loginfo(rospy.get_caller_id() + 'I heard %s', data.data)

def motores():
    # Solo deberia haber un nodo de motores running
    rospy.init_node('motores_nodo', anonymous=False)

    rospy.Subscriber('orden_mov', String, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    motores()
