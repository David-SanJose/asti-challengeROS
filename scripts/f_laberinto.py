#!/usr/bin/env python
from this import d
import rospy
from std_msgs.msg import String
from std_msgs.msg import Int16MultiArray
from asti_prueba.msg import Ldrs

import time

pub = rospy.Publisher('orden_mov', String, queue_size=10)
rospy.init_node('laberinto', anonymous=False)
rate = rospy.Rate(10) # 10hz

ldrs = Ldrs()
UltrSoni2 = Int16MultiArray()
UltrSoni2.data = []
data = []


#Limites de distanciacon las paredes
limites_inf = [15,20,5]
limites_sup = [25]
MAX_LIMITE_EXTREMO = 40
#Contador de ciclos que lleva corrigiendo
contador_ciclos_correcion = 0
contador_ciclos_reconocimiento = 0
# Convenciones para CONSTANTES
IZQ, CEN, DER = [0,1,2]
INDETERMINADO, INFERIOR_AL_LIMITE, CENTRADO_ENTRE_LIMITES, SUPERIOR_AL_LIMITE, EXTREMO_LEJANO_AL_LIMITE = [-99,-1,0,1, 99]
#LISTADO DE ESTADOS
ESTADO_INDETERMINADO, ESTADO_AVANZAR, ESTADO_CORREGIR_IZQ, ESTADO_CORREGIR_DER = ["I","R", "CI", "CD"]
ESTADO_PRE_C_IZQ, ESTADO_PRE_C_DER, ESTADO_RECONOCIMIENTO, ESTADO_POST_RECON = ["P_CI", "P_CD", "REC", "POST-REC"]
ESTADO_FIND_PIZQ_AVANZA, ESTADO_FIND_PIZQ_GIRO, ESTADO_POST_FPIZQ_AV, ESTADO_POST_FPIZQ_GI,  = ["FP-IZQ-A", "FP-IZQ-G", "POST-FP-IZQ-A", "POST-FP-IZQ-G"]
#ACCIONES
A_AVANZAR, A_GIRO_IZQ, A_GIRO_DER, A_ATRAS, A_STOP = ["avanza", "gizq", "gder", "atras", "stop"]
# Lista de acciones segun el ciclo de reconocimiento
LISTA_A_RECONOCIMIENTO = [A_STOP, A_GIRO_IZQ, A_GIRO_IZQ, A_GIRO_DER, A_GIRO_DER,
 A_GIRO_DER, A_GIRO_DER, A_GIRO_IZQ, A_GIRO_IZQ]

def ordenDeMoviviento(movimiento_str):
    pub.publish(movimiento_str)

def subsUltrasonidos(array_data):
    global UltrSoni2
    global data

    UltrSoni2 = array_data
    data = UltrSoni2.data
    #rospy.loginfo(rospy.get_caller_id()+" UltrSoni2 He recibido datos" + str(UltrSoni2.data[0]))

def getEstadoDeRobotConParedIzq(data_fija):
    
    if len(data_fija):
        if data_fija[IZQ] >= MAX_LIMITE_EXTREMO:
            return EXTREMO_LEJANO_AL_LIMITE
        elif data_fija[IZQ] < limites_inf[IZQ]:
            return INFERIOR_AL_LIMITE
        elif data_fija[IZQ] > limites_sup[IZQ]:
            return SUPERIOR_AL_LIMITE
        else:
            return CENTRADO_ENTRE_LIMITES
    else:
        return INDETERMINADO

def accionSegunEstado(estado):
    if estado == ESTADO_AVANZAR:
        ordenDeMoviviento(A_AVANZAR)

    elif estado == ESTADO_PRE_C_IZQ:
        ordenDeMoviviento(A_GIRO_IZQ)
        time.sleep(0.4)

    elif estado == ESTADO_PRE_C_DER:
        ordenDeMoviviento(A_GIRO_DER)
        time.sleep(0.4)

    elif estado == ESTADO_CORREGIR_IZQ:
        ordenDeMoviviento(A_AVANZAR)

    elif estado == ESTADO_CORREGIR_DER:
        ordenDeMoviviento(A_AVANZAR)

    elif estado == ESTADO_INDETERMINADO:
        ordenDeMoviviento(A_STOP)

    elif estado == ESTADO_RECONOCIMIENTO:
        ordenRec = LISTA_A_RECONOCIMIENTO[contador_ciclos_reconocimiento]
        ordenDeMoviviento(ordenRec)
        time.sleep(0.5)
        ordenDeMoviviento(A_STOP)
        time.sleep(0.2)

    elif estado == ESTADO_POST_RECON:
        ordenDeMoviviento(A_STOP)

    elif estado == ESTADO_FIND_PIZQ_AVANZA:
        ordenDeMoviviento(A_AVANZAR)
        time.sleep(2)
        ordenDeMoviviento(A_STOP)
        time.sleep(0.3)

    elif estado == ESTADO_FIND_PIZQ_GIRO:
        ordenDeMoviviento(A_GIRO_IZQ)
        time.sleep(0.5)
        ordenDeMoviviento(A_STOP)
        time.sleep(0.3)

    elif estado == ESTADO_POST_FPIZQ_AV:
        ordenDeMoviviento(A_STOP)
        time.sleep(0.1)
    
    elif estado == ESTADO_POST_FPIZQ_GI:
        ordenDeMoviviento(A_STOP)
        time.sleep(0.1)

    else:
        ordenDeMoviviento(A_STOP)
  
    

def cambiarDeEstado(estado, estado_pared_izq):
    global contador_ciclos_correcion
    global contador_ciclos_reconocimiento
    maximo_cont_correcion = 20

    if (estado != ESTADO_RECONOCIMIENTO and
        estado != ESTADO_POST_RECON and
        estado != ESTADO_FIND_PIZQ_AVANZA and
        estado != ESTADO_FIND_PIZQ_GIRO and 
        estado != ESTADO_POST_FPIZQ_AV and
        estado != ESTADO_POST_FPIZQ_GI and
        estado_pared_izq == EXTREMO_LEJANO_AL_LIMITE): #EN CASO DE ALEJARSE MUCHO, ENTRA EN RECONOCIMIENTO
        return ESTADO_RECONOCIMIENTO

    elif estado == ESTADO_AVANZAR:
        if estado_pared_izq == INFERIOR_AL_LIMITE:
            return ESTADO_PRE_C_DER
        elif estado_pared_izq == SUPERIOR_AL_LIMITE:
            return ESTADO_PRE_C_IZQ

    elif estado == ESTADO_PRE_C_IZQ:
        return ESTADO_CORREGIR_IZQ

    elif estado == ESTADO_PRE_C_DER:
        return ESTADO_CORREGIR_DER

    elif estado == ESTADO_CORREGIR_IZQ:
        if estado_pared_izq == CENTRADO_ENTRE_LIMITES:
            return ESTADO_AVANZAR
        elif estado_pared_izq == INFERIOR_AL_LIMITE:
            return ESTADO_PRE_C_DER
        elif contador_ciclos_correcion >= maximo_cont_correcion:
            contador_ciclos_correcion = 0
            return ESTADO_PRE_C_IZQ

    elif estado == ESTADO_CORREGIR_DER:
        if estado_pared_izq == CENTRADO_ENTRE_LIMITES:
            return ESTADO_AVANZAR
        elif estado_pared_izq == SUPERIOR_AL_LIMITE:
            return ESTADO_PRE_C_IZQ
        elif contador_ciclos_correcion >= maximo_cont_correcion:
            contador_ciclos_correcion = 0
            return ESTADO_PRE_C_DER
    
    elif estado == ESTADO_INDETERMINADO:
        if estado_pared_izq == INFERIOR_AL_LIMITE:
            return ESTADO_PRE_C_DER
        elif estado_pared_izq == SUPERIOR_AL_LIMITE:
            return ESTADO_PRE_C_IZQ
        elif estado_pared_izq == CENTRADO_ENTRE_LIMITES:
            return ESTADO_AVANZAR

    elif estado == ESTADO_RECONOCIMIENTO:
        #print("CICLOS RECON:", contador_ciclos_reconocimiento)
        if estado_pared_izq is not EXTREMO_LEJANO_AL_LIMITE:
            contador_ciclos_reconocimiento += 1
            print("      REC -> AVANZAR")
            return ESTADO_POST_RECON
        if contador_ciclos_reconocimiento < len(LISTA_A_RECONOCIMIENTO) -1:
            contador_ciclos_reconocimiento += 1
            return estado
        else:
            contador_ciclos_reconocimiento = 0
            print("\n\nSE ACABARON LOS CICLOS DE RECONOCIMIENTO\n")
            return ESTADO_FIND_PIZQ_GIRO #Si se acaban los ciclos de recon sin encontrar nada, gira la pared

    elif estado == ESTADO_POST_RECON:
        if estado_pared_izq is not EXTREMO_LEJANO_AL_LIMITE:
            contador_ciclos_reconocimiento = 0
            return ESTADO_INDETERMINADO
        else:
            if contador_ciclos_reconocimiento >= len(LISTA_A_RECONOCIMIENTO):
                contador_ciclos_reconocimiento = 0
                print("\n\nSE ACABARON LOS CICLOS DE RECONOCIMIENTO\n")
                return ESTADO_FIND_PIZQ_GIRO #Si se acaban los ciclos de recon sin encontrar nada, gira la pared
            else:
                return ESTADO_RECONOCIMIENTO

    elif estado == ESTADO_FIND_PIZQ_AVANZA:
        if estado_pared_izq == EXTREMO_LEJANO_AL_LIMITE:
                return ESTADO_RECONOCIMIENTO 
        return ESTADO_POST_FPIZQ_AV

    elif estado == ESTADO_FIND_PIZQ_GIRO:
        if estado_pared_izq == EXTREMO_LEJANO_AL_LIMITE:
                return ESTADO_FIND_PIZQ_AVANZA
        return ESTADO_POST_FPIZQ_GI

    elif estado == ESTADO_POST_FPIZQ_AV:
        if estado_pared_izq is not EXTREMO_LEJANO_AL_LIMITE:
            return ESTADO_INDETERMINADO
        else:
            return ESTADO_RECONOCIMIENTO

    elif estado == ESTADO_POST_FPIZQ_GI:
        if estado_pared_izq is not EXTREMO_LEJANO_AL_LIMITE:
            return ESTADO_INDETERMINADO
        else:
            return ESTADO_FIND_PIZQ_AVANZA

    return estado



def main():
    #Se declara el subscriber de los ultrasonidos
    rospy.Subscriber('Ultrasonidos_data', Int16MultiArray, subsUltrasonidos)
    # Estado en el que se encuentra el robot
    estadoAnt = ESTADO_INDETERMINADO
    estado = ESTADO_INDETERMINADO
    
    
    #Entra al bucle de ROS
    while not rospy.is_shutdown():
        global data
        global contador_ciclos_correcion
        
        
        ######################
        ### AQUI EL CODIGO ###
        print("---  DATA: ",data)

        data_fija = data

        #Comprobacion distancia izq:
        dist_estado_izq = getEstadoDeRobotConParedIzq(data_fija)

        #Accion segun estado
        accionSegunEstado(estado)
        # cambio de estado
        estado = cambiarDeEstado(estado, dist_estado_izq)

        #Incrementar numero de ciclos que lleva corrigiendo a la IZQ el robot
        if estado == ESTADO_CORREGIR_IZQ or estado == ESTADO_CORREGIR_DER:
            contador_ciclos_correcion += 1
        else:
            contador_ciclos_correcion = 0

        try:
            print("ESTADO ACTUAL: ", estado, "   --- DIST: ", data_fija[IZQ])
        except:
            print("ESTADO ACTUAL: ", estado)

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