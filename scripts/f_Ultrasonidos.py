#!/usr/bin/env python
import rospy
from std_msgs.msg import Int16MultiArray

pub = rospy.Publisher('Ultrasonidos_data', Int16MultiArray, queue_size=10)
rospy.init_node('Ultrasonidos_node', anonymous=False)
rate = rospy.Rate(1) # 10hz

def publishUltrasonidos_data(ult_data):
    pub.publish(ult_data)

def mainMockup():
    ult_array = Int16MultiArray()

    i = 0
    while not rospy.is_shutdown():
        ult_array.data = [i]
        rospy.loginfo(rospy.get_caller_id() + "Array ultrason: "+str(ult_array.data[0]))
        publishUltrasonidos_data(ult_array)

        rate.sleep()
        i += 1
    pass

if __name__ == '__main__':
    try:
        mainMockup()
    except rospy.ROSInterruptException:
        pass