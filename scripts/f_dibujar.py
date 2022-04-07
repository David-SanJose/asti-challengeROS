#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from asti_prueba.msg import Ldrs
from std_msgs.msg import Int16

pubMotor = rospy.Publisher('orden_mov', String, queue_size=10)
pubServoBoli = rospy.Publisher('orden_grados_Servo', Int16, queue_size=10)

rospy.init_node('dibujar', anonymous=True)
rate = rospy.Rate(1) # 10hz

ldrs = Ldrs() # Variable con los datos de los LDRs

def ordenDeMoviviento(movimiento_str):
    pubMotor.publish(movimiento_str)

def ordenGradosServo(grados):
    pubServoBoli.publish(grados)

def subsLDRs_data(data):
    global ldrs
    ldrs = data
    rospy.loginfo(rospy.get_caller_id() + "He recibido datos" + str(data.ldr1) + str(ldrs.ldr1))

def main():
    #Se declara el subscriber de los LDR
    rospy.Subscriber('LDRs_data', Ldrs, subsLDRs_data)

    #Entra al bucle de ROS
    while not rospy.is_shutdown():

        ######################
        ### AQUI EL CODIGO ###

        orden = "ORDEN 66" #MODIFICAR
        gradosServo = 20

        ### FIN DEL CODIGO ###


        #Se publica la orden de movimiento 
        ordenDeMoviviento(orden) 
        ordenGradosServo(gradosServo)
        rate.sleep()


    

def mainMockup():
    
    boolBlinkTest = True
    grados = 0

    rospy.Subscriber('LDRs_data', Ldrs, subsLDRs_data)

    while not rospy.is_shutdown():
       
        if ldrs.ldr1:
            debug_str = "a"
        else:
            debug_str = "s"

        grados += 1

        ordenDeMoviviento(debug_str)
        ordenGradosServo(grados)
        rospy.loginfo("Mostrando: " + debug_str + " Grados: %i", grados)
        rate.sleep()

        if grados == 180:
            grados = 0

# CAMBIAR mainMockup por main

if __name__ == '__main__':
    try:
        mainMockup()
    except rospy.ROSInterruptException:
        pass