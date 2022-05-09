#!/usr/bin/env python
import rospy
from std_msgs.msg import Int16

try:
    import RPi.GPIO as GPIO
except:
    import Mock.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(24, GPIO.OUT)

pwm = GPIO.PWM(24, 100)

def AngleToDuty(angulo):
    return float(angulo)/10. + 5.

def callback(data):
    posicion = data.data
    pwm.ChangeDutyCycle(AngleToDuty(posicion))
    print("Cambiando angulo a:", posicion)

    

def motorSERVO():
    # Solo deberia haber un nodo de motores running
    rospy.init_node('servopales_nodo', anonymous=False)

    rospy.Subscriber('orden_grados_Servo', Int16, callback)

    pwm.start(AngleToDuty(0))

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    motorSERVO()
