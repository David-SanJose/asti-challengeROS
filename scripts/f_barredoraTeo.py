#!/usr/bin/env python
from ast import Return
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

#Contador de ciclos que lleva corrigiendo
contador_ciclos_reconocimiento = 0
# Convenciones para CONSTANTES
IZQ, CEN, DER = [0,1,2]
INDETERMINADO, INFERIOR_AL_LIMITE, CENTRADO_ENTRE_LIMITES, SUPERIOR_AL_LIMITE, EXTREMO_LEJANO_AL_LIMITE = [-99,-1,0,1, 99]
#LISTADO DE ESTADOS
ESTADO_INDETERMINADO, ESTADO_AVANZAR, ESTADO_CORREGIR_IZQ, ESTADO_CORREGIR_DER = ["I","R", "CI", "CD"]
ESTADO_RECONOCIMIENTO = "REC"
ESTADO_DES_LATERAL, ESTADO_ATRAS = ["DL", "A"]
ESTADO_PRE_GIRO, ESTADO_GIRO_DER, ESTADO_EMPUJAR, ESTADO_GIRO_BOLAS = ["PG", "GD", "E", "GB"]
#ACCIONES
A_AVANZAR, A_GIRO_IZQ, A_GIRO_DER, A_ATRAS, A_STOP = ["avanza", "gizq", "gder", "atras", "stop"]
A_DESPL_IZQ, A_DESPL_DER = ["mizq", "mder"]
# Lista de acciones segun el ciclo de reconocimiento
LISTA_A_RECONOCIMIENTO = [A_STOP, A_GIRO_IZQ, A_GIRO_IZQ, A_GIRO_DER, A_GIRO_DER,
 A_GIRO_DER, A_GIRO_DER, A_GIRO_IZQ, A_GIRO_IZQ, A_AVANZAR]

#variables
dist_pared_inicial = INDETERMINADO
isOrigenAvanzar = True
#Limites de distanciacon las paredes
limites_inf = [15,20,15] #FIXME
limites_sup = []
MAX_LIMITE_EXTREMO = 80

def ordenDeMoviviento(movimiento_str):
    pub.publish(movimiento_str)

def subsUltrasonidos(array_data):
    global UltrSoni2
    global data

    UltrSoni2 = array_data
    data = UltrSoni2.data
    #rospy.loginfo(rospy.get_caller_id()+" UltrSoni2 He recibido datos" + str(UltrSoni2.data[0]))

def getEstadoDeRobotConPared(data_fija, PARED):
    global MAX_LIMITE_EXTREMO

    if len(data_fija):
        if data_fija[PARED] >= MAX_LIMITE_EXTREMO:
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
    global contador_ciclos_reconocimiento

    if estado == ESTADO_INDETERMINADO:
        ordenDeMoviviento(A_STOP)

    elif estado == ESTADO_AVANZAR:
        ordenDeMoviviento(A_AVANZAR)

    elif estado == ESTADO_CORREGIR_IZQ:
        ordenDeMoviviento(A_DESPL_IZQ)

    elif estado == ESTADO_CORREGIR_DER:
        ordenDeMoviviento(A_DESPL_DER)

    elif estado == ESTADO_DES_LATERAL:
        ordenDeMoviviento(A_DESPL_IZQ)  

    elif estado == ESTADO_PRE_GIRO:
        ordenDeMoviviento(A_AVANZAR)
    
    elif estado == ESTADO_GIRO_DER:
        ordenDeMoviviento(A_GIRO_DER)
        time.sleep(1.7)
    
    elif estado == ESTADO_EMPUJAR:
        ordenDeMoviviento(A_AVANZAR)

    elif estado == ESTADO_ATRAS:
        ordenDeMoviviento(A_ATRAS)

    elif estado == ESTADO_GIRO_BOLAS:
        ordenDeMoviviento(A_GIRO_DER)

    elif estado == ESTADO_RECONOCIMIENTO:
        ordenRec = LISTA_A_RECONOCIMIENTO[contador_ciclos_reconocimiento]
        ordenDeMoviviento(ordenRec)
        time.sleep(0.5)
        ordenDeMoviviento(A_STOP)
        time.sleep(0.2)

    else:
        ordenDeMoviviento(A_STOP)

def cambiarDeEstado(estado, data_fija):
    global dist_pared_inicial, isOrigenAvanzar
    global contador_ciclos_reconocimiento

    estado_izq = getEstadoDeRobotConPared(data_fija, IZQ)
    estado_cen = getEstadoDeRobotConPared(data_fija, CEN)
    print("ESTADO IZQ: ", estado_izq, "\tESTADO CEN: ", estado_cen)

    if estado == ESTADO_INDETERMINADO:
        print("JAJA", dist_pared_inicial, "    ----  JEJE")
        if dist_pared_inicial == INDETERMINADO:
            return ESTADO_INDETERMINADO
        else:
            return ESTADO_AVANZAR

    elif estado == ESTADO_AVANZAR:
        isOrigenAvanzar = True
        if estado_cen == CENTRADO_ENTRE_LIMITES:
            return ESTADO_DES_LATERAL
        elif estado_izq == INFERIOR_AL_LIMITE:
            return ESTADO_CORREGIR_DER
        elif estado_izq == SUPERIOR_AL_LIMITE:
            return ESTADO_CORREGIR_IZQ

    elif estado == ESTADO_CORREGIR_IZQ:
        if estado_izq == CENTRADO_ENTRE_LIMITES:
            if isOrigenAvanzar:
                return ESTADO_AVANZAR
            else:
                return ESTADO_EMPUJAR
        elif estado_izq == INFERIOR_AL_LIMITE:
            return ESTADO_CORREGIR_DER
    
    elif estado == ESTADO_CORREGIR_DER:
        if estado_izq == CENTRADO_ENTRE_LIMITES:
            if isOrigenAvanzar:
                return ESTADO_AVANZAR
            else:
                return ESTADO_EMPUJAR
        elif estado_izq == SUPERIOR_AL_LIMITE:
            return ESTADO_CORREGIR_IZQ

    elif estado == ESTADO_DES_LATERAL:
        if estado_izq == INFERIOR_AL_LIMITE:
            return ESTADO_PRE_GIRO

    elif estado == ESTADO_PRE_GIRO:
        if estado_cen == INFERIOR_AL_LIMITE:
            return ESTADO_GIRO_DER
        
    elif estado == ESTADO_GIRO_DER:
            return ESTADO_EMPUJAR
    
    elif estado == ESTADO_EMPUJAR:
        isOrigenAvanzar = False
        if estado_cen == INFERIOR_AL_LIMITE:
            return ESTADO_ATRAS
        elif estado_izq == INFERIOR_AL_LIMITE:
            return ESTADO_CORREGIR_DER
        elif estado_izq == SUPERIOR_AL_LIMITE:
            return ESTADO_CORREGIR_IZQ

    elif estado == ESTADO_ATRAS:
        if estado_cen == SUPERIOR_AL_LIMITE:
            return ESTADO_GIRO_BOLAS
        # FIXME de momento innecesario
        elif estado_cen == MAX_LIMITE_EXTREMO:
            return ESTADO_EMPUJAR
    
    elif estado == ESTADO_GIRO_BOLAS:
        # FIXME ver si poner sleeps o dejarlo asi
        if estado_cen == SUPERIOR_AL_LIMITE and estado_izq == CENTRADO_ENTRE_LIMITES:
            return ESTADO_AVANZAR

    return estado


def main():
    #Se declara el subscriber de los ultrasonidos
    rospy.Subscriber('Ultrasonidos_data', Int16MultiArray, subsUltrasonidos)
    # Estado en el que se encuentra el robot
    estado = ESTADO_INDETERMINADO 

    global data, dist_pared_inicial
    global limites_sup
    
    while dist_pared_inicial == INDETERMINADO:
        if len(data):
            data_fija = data
            print("DAFIJA: ", data_fija)
            dist_pared_inicial = data_fija[IZQ]

    limites_sup = [dist_pared_inicial + 10, 40, dist_pared_inicial + 10]
    print("\n\n------------------LIMITE SUPERIOR: ", limites_sup)
    #Entra al bucle de ROS
    while not rospy.is_shutdown():       
        
        ######################
        ### AQUI EL CODIGO ###
        print("---  DATA: ",data)

        data_fija = data

        #Accion segun estado
        accionSegunEstado(estado)
        # cambio de estado
        estado = cambiarDeEstado(estado, data_fija)

        print("ESTADO ACTUAL: ", estado)

        rate.sleep()
       

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass