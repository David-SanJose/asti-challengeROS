#!/usr/bin/env python
import rospy
from scripts.f_barredoraTeo import ESTADO_CORREGIR_IZQ, ESTADO_INDETERMINADO, ESTADO_RECONOCIMIENTO
from scripts.f_laberinto import ESTADO_CORREGIR_DER
from std_msgs.msg import String
from std_msgs.msg import Int16MultiArray
from asti_prueba.msg import Ldrs

import time

pub = rospy.Publisher('orden_mov', String, queue_size=10)
rospy.init_node('bolos_node', anonymous=False)
rate = rospy.Rate(10) # 10hz

ldrs = Ldrs()
UltrSoni2 = Int16MultiArray()
data = []

# Otras variables
estadoAnterior = ESTADO_INDETERMINADO

#Limites de distanciacon las paredes
limites_inf = [8,20, 15]
limites_sup = [60,99999, 25]
MAX_LIMITE_EXTREMO = [60,999999,40]
# Convenciones para CONSTANTES
IZQ, CEN, DER = [0,1,2]
INDETERMINADO, INFERIOR_AL_LIMITE, CENTRADO_ENTRE_LIMITES, SUPERIOR_AL_LIMITE, EXTREMO_LEJANO_AL_LIMITE = [-99,-1,0,1, 99]
#Estado
ESTADO_INDETERMINADO, ESTADO_AVANZAR_1, ESTADO_CORREGIR_IZQ, ESTADO_CORREGIR_DER, ESTADO_GIRO_IZQ = ["I", "A1", "CI", "CD", "GI"]
ESTADO_AVANZAR_2, ESTADO_MOV_IZQ, ESTADO_DISPARAR = ["A2", "MI", "SHOOT"]
ESTADO_RECONOCIMIENTO = ["REC"]

#ACCIONES
A_AVANZAR, A_GIRO_IZQ, A_GIRO_DER, A_ATRAS, A_STOP, A_MOV_IZQ, A_MOV_DER = ["avanza", "gizq", "gder", "atras", "stop", "mizq", "mder"]
# Lista de acciones segun el ciclo de reconocimiento




def ordenDeMoviviento(movimiento_str):
    pub.publish(movimiento_str)

def subsLDRs_data(data):
    global ldrs
    ldrs = data
    rospy.loginfo(rospy.get_caller_id()+" LDR He recibido datos" + str(data.ldr1) + str(ldrs.ldr1))

def subsUltrasonidos(array_data):
    global UltrSoni2
    global data

    UltrSoni2 = array_data
    data = UltrSoni2.data
    #rospy.loginfo(rospy.get_caller_id()+" UltrSoni2 He recibido datos" + str(UltrSoni2.data[0]))

def getEstadoDePosicionConPared(data_fija, PARED):
    if len(data_fija):
        if data_fija[PARED] >= MAX_LIMITE_EXTREMO[PARED]:
            return EXTREMO_LEJANO_AL_LIMITE
        elif data_fija[PARED] < limites_inf[PARED]:
            return INFERIOR_AL_LIMITE
        elif data_fija[PARED] > limites_sup[PARED]:
            return SUPERIOR_AL_LIMITE
        else:
            return CENTRADO_ENTRE_LIMITES
    else:
        return INDETERMINADO

def accionSegunEstado(estado):
    if estado == ESTADO_INDETERMINADO:
        ordenDeMoviviento(A_STOP)
    
    elif estado == ESTADO_AVANZAR_1:
        ordenDeMoviviento(A_AVANZAR)
    
    elif estado == ESTADO_CORREGIR_IZQ:
        ordenDeMoviviento(A_MOV_IZQ)

    elif estado == ESTADO_CORREGIR_DER:
        ordenDeMoviviento(A_MOV_DER)

    elif estado == ESTADO_GIRO_IZQ:
        print("> GIRANDO A LA IZQUIERDA")
        ordenDeMoviviento(A_STOP)
        time.sleep(1)
        ordenDeMoviviento(A_GIRO_IZQ)
        time.sleep(1.7)

    elif estado == ESTADO_AVANZAR_2:
        ordenDeMoviviento(A_AVANZAR)
    
    elif estado == ESTADO_MOV_IZQ:
        ordenDeMoviviento(A_MOV_IZQ)



def cambiarDeEstado(estado, lista_estados_pared):
    global estadoAnterior

    estado_pared_izq = lista_estados_pared[0]
    estado_pared_cen = lista_estados_pared[1]
    estado_pared_der = lista_estados_pared[2]

    if estado == ESTADO_INDETERMINADO:
        if estado_pared_der == INFERIOR_AL_LIMITE:
            return ESTADO_CORREGIR_IZQ
        elif estado_pared_der == SUPERIOR_AL_LIMITE:
            return ESTADO_CORREGIR_DER
        elif estado_pared_der == CENTRADO_ENTRE_LIMITES:
            return ESTADO_AVANZAR_1
    
    if estado == ESTADO_AVANZAR_1:
        if estado_pared_izq == EXTREMO_LEJANO_AL_LIMITE:
            return ESTADO_GIRO_IZQ
        elif estado_pared_der == INFERIOR_AL_LIMITE:
            return ESTADO_CORREGIR_IZQ
        elif estado_pared_der == SUPERIOR_AL_LIMITE:
            return ESTADO_CORREGIR_DER

    if estado == ESTADO_CORREGIR_IZQ:
        if estado_pared_der != INFERIOR_AL_LIMITE:
            return estadoAnterior
    
    if estado == ESTADO_CORREGIR_DER:
        #posible problema con extremo ?
        if estado_pared_der != SUPERIOR_AL_LIMITE:
            return estadoAnterior

    if estado == ESTADO_GIRO_IZQ:
        return ESTADO_AVANZAR_2

    if estado == ESTADO_AVANZAR_2:
        # TODO AQUI VA condicion de LDRS
        if estado_pared_der == INFERIOR_AL_LIMITE:
            return ESTADO_CORREGIR_IZQ
        elif estado_pared_der == SUPERIOR_AL_LIMITE:
            return ESTADO_CORREGIR_DER

    





    return estado

def main():
    #Se declara el subscriber del Ultrasonido
    rospy.Subscriber('Ultrasonidos_data', Int16MultiArray, subsUltrasonidos)

    # Estado en el que se encuentra el robot
    global estadoAnterior
    estado = ESTADO_INDETERMINADO


    #Entra al bucle de ROS
    while not rospy.is_shutdown():
        global data

        ######################
        ### AQUI EL CODIGO ###
        data_fija = data

        #Comprobacion distancia izq:
        dist_estado_izq = getEstadoDePosicionConPared(data_fija, IZQ)
        dist_estado_cen = getEstadoDePosicionConPared(data_fija, CEN)
        dist_estado_der = getEstadoDePosicionConPared(data_fija, DER)

        #Accion segun estado
        accionSegunEstado(estado)
        # cambio de estado
        estadoAnterior = estado
        estado = cambiarDeEstado(estado, [dist_estado_izq, dist_estado_cen, dist_estado_der])
        
        try:
            print("ESTADO ACTUAL: ", estado, "   --- DIST: ", data_fija[IZQ])
        except:
            print("ESTADO ACTUAL: ", estado)
        ### FIN DEL CODIGO ###

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