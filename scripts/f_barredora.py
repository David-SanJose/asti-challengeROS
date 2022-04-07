#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from std_msgs.msg import Int16MultiArray
from asti_prueba.msg import Ldrs

pub = rospy.Publisher('orden_mov', String, queue_size=10)
rospy.init_node('barredora_node', anonymous=False)
rate = rospy.Rate(1) # 10hz

ldrs = Ldrs()
UltrSoni2 = Int16MultiArray()
UltrSoni2.data = []

def ordenDeMoviviento(movimiento_str):
    pub.publish(movimiento_str)

def subsLDRs_data(data):
    global ldrs
    ldrs = data
    rospy.loginfo(rospy.get_caller_id()+" LDR He recibido datos" + str(data.ldr1) + str(ldrs.ldr1))

def subsUltrasonidos(array_data):
    global UltrSoni2
    UltrSoni2 = array_data
    rospy.loginfo(rospy.get_caller_id()+" UltrSoni2 He recibido datos" + str(UltrSoni2.data[0]))

def main():
    #Se declara el subscriber de los LDR
    rospy.Subscriber('Ultrasonidos_data', Int16MultiArray, subsUltrasonidos)

    #Entra al bucle de ROS
    while not rospy.is_shutdown():

        ######################
        ### AQUI EL CODIGO ###

        orden = "ORDEN 66" #MODIFICAR

        ### FIN DEL CODIGO ###


        #Se publica la orden de movimiento 
        ordenDeMoviviento(orden) 
        rate.sleep()

def mainMockup():
    
    boolBlinkTest = True
    rospy.Subscriber('Ultrasonidos_data', Int16MultiArray, subsUltrasonidos)
    
    while not rospy.is_shutdown():
       
        if len(UltrSoni2.data) > 0:
            if UltrSoni2.data[0] == 0:
                debug_str = "a"
            else:
                debug_str = "s"
            ordenDeMoviviento(debug_str)
            rospy.loginfo("Mostrando:" + debug_str)
        rate.sleep()

        

if __name__ == '__main__':
    try:
        mainMockup()
    except rospy.ROSInterruptException:
        pass