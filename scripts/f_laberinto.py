#!/usr/bin/env python
import rospy
from std_msgs.msg import String
from std_msgs.msg import Int16MultiArray
from asti_prueba.msg import Ldrs

import time

pub = rospy.Publisher('orden_mov', String, queue_size=10)
rospy.init_node('laberinto', anonymous=False)
rate = rospy.Rate(1) # 10hz

ldrs = Ldrs()
UltrSoni2 = Int16MultiArray()
UltrSoni2.data = []
data = []
registro = [0,0,0]

# Estado en el que se encuentra el robot
estadoAnt = "R"
estado = "R"

#Limites de distanciacon las paredes
limites_inf = [15,20,5]
limites_sup = [25]
# Convenciones para CONSTANTES
IZQ, CEN, DER = [0,1,2]
INFERIOR_AL_LIMITE, CENTRADO_ENTRE_LIMITES, SUPERIOR_AL_LIMITE = [-1,0,1]

def ordenDeMoviviento(movimiento_str):
    pub.publish(movimiento_str)

def subsUltrasonidos(array_data):
    global UltrSoni2
    global data
    global registro

    UltrSoni2 = array_data
    registro = data
    data = UltrSoni2.data
    rospy.loginfo(rospy.get_caller_id()+" UltrSoni2 He recibido datos" + str(UltrSoni2.data[0]))

def getEstadoDeRobotConParedIzq(data_fija):
    if data_fija[IZQ] < limites_inf[IZQ]:
        return INFERIOR_AL_LIMITE
    elif data_fija[IZQ] > limites_sup[IZQ]:
        return SUPERIOR_AL_LIMITE
    else:
        return CENTRADO_ENTRE_LIMITES

def main():
    #Se declara el subscriber de los ultrasonidos
    rospy.Subscriber('Ultrasonidos_data', Int16MultiArray, subsUltrasonidos)

    
    #Entra al bucle de ROS
    while not rospy.is_shutdown():
        global data
        
        ######################
        ### AQUI EL CODIGO ###
        orden = "stop"
        print("REG. ",registro, "---  DATA: ",data)

        data_fija = data

        #Comprobacion distancia izq:
        dist_estado_izq = getEstadoDeRobotConParedIzq(data_fija)

        # Accion segun estado y cambio de estado
        if estado == "R":
            if dist_estado_izq == INFERIOR_AL_LIMITE:
                estado = "CD"
            elif dist_estado_izq == SUPERIOR_AL_LIMITE:
                estado = "CD"
        elif estado == "CI":
            if dist_estado_izq == CENTRADO_ENTRE_LIMITES:
                estado = "R"
        elif estado == "CD":
            if dist_estado_izq == CENTRADO_ENTRE_LIMITES:
                estado = "R"

        estadoAnt = estado
        print("ESTADO ACTUAL: ", estado, "   --- DIST: ", data_fija[IZQ])

        #Seguir pared de izquierda

        '''
        if len(data) == 3:
            if data[IZQ] <= limites_inf[IZQ]:
                if registro[IZQ] >= data[IZQ]:
                    ordenDeMoviviento("gder")
                    time.sleep(0.2)
                    ordenDeMoviviento("stop")
                    time.sleep(1)
                    ordenDeMoviviento("avanza")
                    time.sleep(1.5)
                    ordenDeMoviviento("stop")
                    time.sleep(1)
                else:
                    ordenDeMoviviento("avanza")
                
            elif data[IZQ] >= limites_sup[IZQ]:
                if registro[IZQ] <= data[IZQ]:
                    ordenDeMoviviento("gizq")
                    time.sleep(0.2)
                    ordenDeMoviviento("stop")
                    time.sleep(1)
                    ordenDeMoviviento("avanza")
                    time.sleep(0.8)
                    ordenDeMoviviento("stop")
                    time.sleep(1)
                else:
                    ordenDeMoviviento("avanza")
            else:
                ordenDeMoviviento("avanza")

        '''

        ''' Prueba 1
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
        '''
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