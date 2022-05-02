#!/usr/bin/env python
from this import d
import rospy
from std_msgs.msg import String
from std_msgs.msg import Int16MultiArray

import time

pub = rospy.Publisher('orden_mov', String, queue_size=10)
rospy.init_node('barredora', anonymous=False)
rate = rospy.Rate(10) # 10hz

UltrSoni2 = Int16MultiArray()
UltrSoni2.data = []
data = []

#Limites de distanciacon las paredes
limites_inf = [15,20,5]
limites_sup = [90,25]
MAX_LIMITE_EXTREMO = 40
#Contador de ciclos que lleva corrigiendo
contador_ciclos_correcion = 0
contador_ciclos_reconocimiento = 0
# Otras variables
desplazamiento_final = False
ladoInicial = 1
ladoContrario = 1
timer_start = 0
timer_distancia = 0
# Convenciones para CONSTANTES
IZQ, CEN, DER = [0,1,2]
INDETERMINADO, INFERIOR_AL_LIMITE, CENTRADO_ENTRE_LIMITES, SUPERIOR_AL_LIMITE, EXTREMO_LEJANO_AL_LIMITE = [-99,-1,0,1, 99]
#LISTADO DE ESTADOS
ESTADO_INDETERMINADO, ESTADO_AVANZAR, ESTADO_CORREGIR_IZQ, ESTADO_CORREGIR_DER = ["I","R", "CI", "CD"]
ESTADO_PRE_C_IZQ, ESTADO_PRE_C_DER, ESTADO_RECONOCIMIENTO, ESTADO_POST_RECON = ["P_CI", "P_CD", "REC", "POST-REC"]
ESTADO_DISM_VEL, ESTADO_DES_LATERAL, ESTADO_ATRAS = ["DV", "DL", "A"]
#ACCIONES
A_AVANZAR, A_GIRO_IZQ, A_GIRO_DER, A_ATRAS, A_STOP = ["avanza", "gizq", "gder", "atras", "stop"]
A_DESPL_IZQ, A_DESPL_DER = ["mizq", "mder"]
# Lista de acciones segun el ciclo de reconocimiento
LISTA_A_RECONOCIMIENTO = [A_STOP, A_GIRO_IZQ, A_GIRO_IZQ, A_GIRO_DER, A_GIRO_DER,
 A_GIRO_DER, A_GIRO_DER, A_GIRO_IZQ, A_GIRO_IZQ, A_AVANZAR]

def ordenDeMoviviento(movimiento_str):
    pub.publish(movimiento_str)

def subsUltrasonidos(array_data):
    global UltrSoni2
    global data

    UltrSoni2 = array_data
    data = UltrSoni2.data
    #rospy.loginfo(rospy.get_caller_id()+" UltrSoni2 He recibido datos" + str(UltrSoni2.data[0]))

def getDistanciaInicialRobotRespectoPared(data_fija):
    global ladoInicial
    global ladoContrario

    if len(data_fija):
        if data_fija[IZQ] > data_fija[DER]:
            ladoInicial = DER
            ladoContrario = IZQ
            return data_fija[DER]
        elif data_fija[DER] > data_fija[IZQ]:
            ladoInicial = IZQ
            ladoContrario = DER
            return data_fija[IZQ]
        else:
            print("LAS DOS DISTANCIAS SON IGUALES, TONTO")
            return INDETERMINADO
    else:
        print("NO HAY DATOS, TONTO x2")
        return INDETERMINADO

def accionSegunEstado(estado, dist_pared_lateral_mas_cercana, data_fija):
    global desplazamiento_final

    if estado == ESTADO_AVANZAR:
        ordenDeMoviviento(A_AVANZAR)

    elif estado == ESTADO_INDETERMINADO:
        if dist_pared_lateral_mas_cercana == INDETERMINADO or desplazamiento_final == True:
            ordenDeMoviviento(A_STOP)

    elif estado == ESTADO_ATRAS:
        desplazamiento_final = False
        ordenDeMoviviento(A_ATRAS)
        time.sleep(timer_distancia)

    elif estado == ESTADO_DES_LATERAL:
        if desplazamiento_final:
            #moverse hacia el lado por el que empezamos la prueba
            if ladoInicial == IZQ:
                ordenDeMoviviento(A_DESPL_IZQ)
            elif ladoInicial == DER:
                ordenDeMoviviento(A_DESPL_DER)
        else:
            # moverse hacia el lado contrario
            desplazamiento_final = True
            if ladoContrario == IZQ:
                ordenDeMoviviento(A_DESPL_IZQ)
            elif ladoContrario == DER:
                ordenDeMoviviento(A_DESPL_DER)
    
    elif estado == ESTADO_DISM_VEL:
        # TODO cambiar velocidad
        pass

    else:
        ordenDeMoviviento(A_STOP)

def cambiarDeEstado(estado, dist_pared_lateral_mas_cercana, data_fija):
    global timer_start, timer_distancia, desplazamiento_final

    if estado == ESTADO_AVANZAR:
        if data_fija[CEN] < limites_sup[CEN] and data_fija[CEN] > limites_inf[CEN]:
            return ESTADO_DISM_VEL
    
    elif estado == ESTADO_INDETERMINADO:
        print("JAJA", dist_pared_lateral_mas_cercana, "    ----  JEJE", desplazamiento_final)
        if dist_pared_lateral_mas_cercana == INDETERMINADO or desplazamiento_final == True:
            return ESTADO_INDETERMINADO
        else:
            timer_start = time.time()
            return ESTADO_AVANZAR

    elif estado == ESTADO_ATRAS:
        timer_distancia = timer_start - time.time()
        desplazamiento_final = False
        return ESTADO_DES_LATERAL

    elif estado == ESTADO_DES_LATERAL:
        if desplazamiento_final and data_fija[ladoInicial] <= INFERIOR_AL_LIMITE:
            return ESTADO_INDETERMINADO
        elif not desplazamiento_final and data_fija[ladoContrario] <= dist_pared_lateral_mas_cercana:
            desplazamiento_final = True
            return ESTADO_AVANZAR
    
    elif estado == ESTADO_DISM_VEL:
        if data_fija[CEN] == INFERIOR_AL_LIMITE:
            if desplazamiento_final:
                return ESTADO_DES_LATERAL
            else: 
                return ESTADO_ATRAS

    return estado



def main():
    #Se declara el subscriber de los ultrasonidos
    rospy.Subscriber('Ultrasonidos_data', Int16MultiArray, subsUltrasonidos)
    # Estado en el que se encuentra el robot
    estado = ESTADO_INDETERMINADO
    dist_pared_lateral_mas_cercana = INDETERMINADO   
    global data 
    print("AAAAAAAAAAAAAAAAAAAA", "\n"*10)
    while dist_pared_lateral_mas_cercana == INDETERMINADO:
        data_fija = data
        print("DAFIJA: ", data_fija)
        dist_pared_lateral_mas_cercana = getDistanciaInicialRobotRespectoPared(data_fija)

    #Entra al bucle de ROS
    while not rospy.is_shutdown():
        
        
        ######################
        ### AQUI EL CODIGO ###
        print("---  DATA: ",data)

        data_fija = data

        

        #Accion segun estado
        accionSegunEstado(estado, dist_pared_lateral_mas_cercana, data_fija)
        # cambio de estado
        estado = cambiarDeEstado(estado, dist_pared_lateral_mas_cercana, data_fija)

        print("ESTADO ACTUAL: ", estado)

        rate.sleep()
       

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass