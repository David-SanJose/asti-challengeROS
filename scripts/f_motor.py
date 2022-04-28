#!/usr/bin/env python
import rospy
from std_msgs.msg import String

try:
    import RPi.GPIO as GPIO
except:
    import Mock.GPIO as GPIO

MOTORES_DIC = {
    "FL":[9,10],
    "FR":[3,2],
    "BR":[4,17],
    "BL":[27,22]
}
ENABLE = 18

def move_motor(motor, reverse):
    global MOTORES_DIC
    GPIO.output(MOTORES_DIC[motor][0], not reverse)
    GPIO.output(MOTORES_DIC[motor][1], reverse)

def stop_motor(motor):
    GPIO.output(MOTORES_DIC[motor][0], GPIO.LOW)
    GPIO.output(MOTORES_DIC[motor][1], GPIO.LOW)

def callback(data):
    orden = data.data
    rospy.loginfo(rospy.get_caller_id() + 'ORDEN->    %s', data.data)
    print("Orden recibida:",str(orden),"_")
    if orden == "avanza":
        for key in MOTORES_DIC.keys():
            move_motor(key, 0)
    elif orden == "atras":
        for key in MOTORES_DIC.keys():
            move_motor(key, 1)
    elif orden == "gizq":
        move_motor("FL", 1)
        move_motor("FR", 0)
        move_motor("BL", 1)
        move_motor("BR", 0)
    elif orden == "gder":
        move_motor("FL", 0)
        move_motor("FR", 1)
        move_motor("BL", 0)
        move_motor("BR", 1)
    elif orden == "mizq":
        move_motor("FL", 0)
        move_motor("FR", 1)
        move_motor("BL", 1)
        move_motor("BR", 0)
    elif orden == "mder":
        move_motor("FL", 1)
        move_motor("FR", 0)
        move_motor("BL", 0)
        move_motor("BR", 1)
    elif orden == "FL":
        move_motor("FL", 0)
    elif orden == "FR":
        move_motor("FR", 0)
    elif orden == "BL":
        move_motor("BL", 0)
    elif orden == "BR":
        move_motor("BR", 0)
    elif orden == "FLi":
        move_motor("FL", 1)
    elif orden == "FRi":
        move_motor("FR", 1)
    elif orden == "BLi":
        move_motor("BL", 1)
    elif orden == "BRi":
        move_motor("BR", 1)
    elif orden == "stop":
        for key in MOTORES_DIC.keys():
            stop_motor(key)




def motores():
    global MOTORES_DIC
    global ENABLE

    GPIO.setmode(GPIO.BCM)
    print("Comenzar config")
    # Configuramos los pines como entradas y salidas
    for val in MOTORES_DIC.values():
        for i in val:
            GPIO.setup(i,GPIO.OUT)
            print("PIN: ",i,"en salida/out")

    GPIO.setup(ENABLE,GPIO.OUT)

    p = GPIO.PWM(ENABLE, 50)  # Creamos la instancia PWM con el GPIO a utilizar y la frecuencia de la seÃ±al PWM
    p.start(0)
    GPIO.output(ENABLE,GPIO.HIGH)
    p.ChangeDutyCycle(100)

    print("Fin config")

    # Solo deberia haber un nodo de motores running
    rospy.init_node('motores_nodo', anonymous=False)

    rospy.Subscriber('orden_mov', String, callback)

    # spin() simply keeps python from exiting until this node is stopped
    rospy.spin()

if __name__ == '__main__':
    motores()
