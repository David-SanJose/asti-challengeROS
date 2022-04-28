#!/usr/bin/env python
from select import select
import rospy
from std_msgs.msg import String
import time

pub = rospy.Publisher('orden_mov', String, queue_size=10)
rospy.init_node('mov_libre', anonymous=False)
rate = rospy.Rate(1) # 10hz

def main():
    orders = {
        "w": "avanza",
        "a": "gizq",
        "d": "gder",
        "s": "atras",
        "q": "mizq",
        "e": "mder",
        "": "stop",
        "fl": "FL",
        "fr": "FR",
        "bl": "BL",
        "br": "BR",
        "fli": "FLi",
        "fri": "FRi",
        "bli": "BLi",
        "bri": "BRi"
    }
    while not rospy.is_shutdown():
        select = str(raw_input("aa:\n"))

        if select in orders:
            pub.publish(orders[select])
        else:
            pub.publish("stop")


if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass