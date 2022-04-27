#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from std_msgs.msg import Int16MultiArray
from asti_prueba.msg import Ldrs

pub = rospy.Publisher('orden_mov', String, queue_size=10)
rospy.init_node('laberinto', anonymous=False)
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
    #Se declara el subscriber de los ultrasonidos
    rospy.Subscriber('Ultrasonidos_data', Int16MultiArray, subsUltrasonidos)

    limites_inf = [5,10,5]
    limites_sup = [15]
    IZQ, CEN, DER = [0,1,2]
    #Entra al bucle de ROS
    while not rospy.is_shutdown():

        data = UltrSoni2.data
        ######################
        ### AQUI EL CODIGO ###
        orden = "stop"
        if len(data) == 3:
            if data[DER] <= limites_inf[DER]: #Si se pega a la derecha
                orden = "mizq"
            elif data[IZQ] <= limites_inf[IZQ]: #Si se pega a la izq
                orden = "mder"
            elif data[IZQ] >= limites_sup[IZQ]: #Si se separa de la izq
                orden = "mizq"
            elif data[CEN] <= limites_inf[CEN]: #Si encuentra pared
                orden = "gder"
            else:
                orden = "avanza"

        ### FIN DEL CODIGO ###
        rospy.loginfo("Orden:" + orden)
        #Se publica la orden de movimiento 
        ordenDeMoviviento(orden) 
        rate.sleep()

def mainMockup():
    
    boolBlinkTest = True
    rospy.Subscriber('Ultrasonidos_data', Int16MultiArray, subsUltrasonidos)
    
    while not rospy.is_shutdown():
       
        if len(UltrSoni2.data) > 0:
            if UltrSoni2.data[0]%2 == 0:
                debug_str = "a"
            else:
                debug_str = "s"
            ordenDeMoviviento(debug_str)
            rospy.loginfo("Mostrando:" + debug_str)
        rate.sleep()

        

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass