#!/usr/bin/env python
import rospy
import time
from std_msgs.msg import Int16MultiArray
try:
    import RPi.GPIO as GPIO
except:
    import Mock.GPIO as GPIO


pub = rospy.Publisher('Ultrasonidos_data', Int16MultiArray, queue_size=10)
rospy.init_node('Ultrasonidos_node', anonymous=False)
rate = rospy.Rate(1) # 10hz

GPIO_USON = {"IZQ": [12,19],
            "CEN": [12,13],
            "DER": [12,26]}

def publishUltrasonidos_data(ult_data):
    pub.publish(ult_data)

def mainMockup():
    ult_array = Int16MultiArray()

    i = [3,0,3]
    while not rospy.is_shutdown():
        ult_array.data = i
        rospy.loginfo(rospy.get_caller_id() + "Array ultrason: "+str(ult_array.data[0]))
        publishUltrasonidos_data(ult_array)

        rate.sleep()
        i[0] += 1
        i[1] += 1
        i[2] += 1

        max_i = [20, 100, 60]
        for x in range(3):
            if i[x] > max_i[x]:
                i[x] = 5


def main():
    GPIO.setmode(GPIO.BCM)

    # Definimos los pines que vamos a usar
    global GPIO_USON

    # Configuramos los pines como entradas y salidas

    for key in GPIO_USON.keys():
        GPIO.setup(GPIO_USON[key][0],GPIO.OUT)  # Trigger
        GPIO.setup(GPIO_USON[key][1],GPIO.IN)      # Echo
    ult_array = Int16MultiArray()

    rospy.loginfo("holaaa")
    print("hola en python")

    while not rospy.is_shutdown():
        print("empezando bucle")
        ult_array.data = []
        for key in GPIO_USON.keys():
            distancia = int(medida(GPIO_USON[key]))
            print("La distancia es:   ",distancia)
            ult_array.data.append(distancia)
            time.sleep(0.01)


        #rospy.loginfo(rospy.get_caller_id() + "Array ultrason: "+str(ult_array.data[0]))
        publishUltrasonidos_data(ult_array)

        rate.sleep()

    print("ha acabado")

def medida(uson_list):

    pre_launch = time.time()
    # Esta funcion mide una distancia
    GPIO.output(uson_list[0], True)
    time.sleep(0.00001)
    GPIO.output(uson_list[0], False)
    start = time.time()
    
    keep_going = True

    while GPIO.input(uson_list[1])==0 and keep_going:
        start = time.time()
        print("start", start)
        if start - pre_launch > 1:
            keep_going = False


    while GPIO.input(uson_list[1])==1 and keep_going:
        stop = time.time()
        if stop - pre_launch > 1:
            keep_going = False

    elapsed = stop-start
    distancia = (elapsed * 34300)/2

    return distancia


if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass

