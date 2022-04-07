#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from asti_prueba.msg import Ldrs

pub = rospy.Publisher('LDRs_data', Ldrs, queue_size=10)
rospy.init_node('LDRs_node', anonymous=True)
rate = rospy.Rate(1) # 10hz

def publishLDR_data(ldr_data):
    pub.publish(ldr_data)

def mainMockup():
    ldrs = Ldrs()
    boolBlinkTest = True
    while not rospy.is_shutdown():
        ldrs.ldr1 = boolBlinkTest
        ldrs.ldr2 = not boolBlinkTest
        rospy.loginfo("bool:"+str(ldrs.ldr1))
        boolBlinkTest = not boolBlinkTest

        publishLDR_data(ldrs)
        rospy.loginfo(rospy.get_caller_id()+ " Mostrando:" + str(ldrs.ldr1))
        rate.sleep()
    pass

if __name__ == '__main__':
    try:
        mainMockup()
    except rospy.ROSInterruptException:
        pass