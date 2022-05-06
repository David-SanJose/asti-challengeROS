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
distanciasReconocimiento = []

#Contador de ciclos que lleva corrigiendo
contador_ciclos_reconocimiento = 0
# Convenciones para CONSTANTES
IZQ, CEN, DER = [0,1,2]
INDETERMINADO, EXTREMO_CERCANO_PARED ,INFERIOR_AL_LIMITE, CENTRADO_ENTRE_LIMITES, SUPERIOR_AL_LIMITE, EXTREMO_LEJANO_AL_LIMITE = [-99,-2,-1,0,1, 99]
#LISTADO DE ESTADOS
ESTADO_INDETERMINADO, ESTADO_AVANZAR, ESTADO_CORREGIR_IZQ, ESTADO_CORREGIR_DER = ["I","R", "CI", "CD"]
ESTADO_RECONOCIMIENTO, ESTADO_POST_RECON = ["REC", "POST-REC"]
ESTADO_DES_LATERAL, ESTADO_RECOLOCACION = ["DL", "RCOL"]
ESTADO_PRE_GIRO, ESTADO_GIRO_DER, ESTADO_EMPUJAR, ESTADO_GIRO_BOLAS = ["PG", "GD", "E", "GB"]
#ACCIONES
A_AVANZAR, A_GIRO_IZQ, A_GIRO_DER, A_ATRAS, A_STOP = ["avanza", "gizq", "gder", "atras", "stop"]
A_DESPL_IZQ, A_DESPL_DER = ["mizq", "mder"]
# Lista de acciones segun el ciclo de reconocimiento
LISTA_A_RECONOCIMIENTO = [A_STOP, A_GIRO_IZQ, A_GIRO_IZQ, A_GIRO_DER, A_GIRO_DER,
 A_GIRO_DER, A_GIRO_DER, A_GIRO_IZQ, A_GIRO_IZQ]

#variables
dist_pared_inicial = INDETERMINADO
isOrigenAvanzar = True
estadoAnteriorAReconocimiento = ESTADO_INDETERMINADO
posicionDistanciaElegidaRec = -1

#Limites de distanciacon las paredes
MIN_LIMITE_EXTREMO = [15, -99999, -99999]
limites_inf = [] #FIXME
limites_sup = []
MAX_LIMITE_EXTREMO = []

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
        if data_fija[PARED] >= MAX_LIMITE_EXTREMO[PARED]:
            return EXTREMO_LEJANO_AL_LIMITE

        elif data_fija[PARED] > limites_sup[PARED]:
            return SUPERIOR_AL_LIMITE

        elif data_fija[PARED] > limites_inf[PARED]:
            return CENTRADO_ENTRE_LIMITES
        
        elif data_fija[PARED] > MIN_LIMITE_EXTREMO[PARED]:
            return INFERIOR_AL_LIMITE
        
        elif data_fija[PARED] < MIN_LIMITE_EXTREMO[PARED]:
            return EXTREMO_CERCANO_PARED

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

    elif estado == ESTADO_GIRO_BOLAS:
        ordenDeMoviviento(A_GIRO_DER)
        time.sleep(1.7)

    elif estado == ESTADO_RECOLOCACION:
        ordenDeMoviviento(A_STOP)

    elif estado == ESTADO_RECONOCIMIENTO:
        ordenRec = LISTA_A_RECONOCIMIENTO[contador_ciclos_reconocimiento]
        print("\n+++++++++++RECON: ", contador_ciclos_reconocimiento)
        ordenDeMoviviento(ordenRec)
        time.sleep(0.5)
        ordenDeMoviviento(A_STOP)
        time.sleep(0.2)
    
    elif estado == ESTADO_POST_RECON:
        ordenRec = LISTA_A_RECONOCIMIENTO[contador_ciclos_reconocimiento]
        print("\n+++++++++++POST: ", contador_ciclos_reconocimiento)
        ordenDeMoviviento(ordenRec)
        time.sleep(0.5)
        ordenDeMoviviento(A_STOP)
        time.sleep(0.2)

    else:
        ordenDeMoviviento(A_STOP)

def cambiarDeEstado(estado, data_fija):
    global dist_pared_inicial, isOrigenAvanzar
    global contador_ciclos_reconocimiento
    global estadoAnteriorAReconocimiento
    global posicionDistanciaElegidaRec
    global distanciasReconocimiento

    estado_izq = getEstadoDeRobotConPared(data_fija, IZQ)
    estado_cen = getEstadoDeRobotConPared(data_fija, CEN)
    print("ESTADO IZQ: ", estado_izq, "\tESTADO CEN: ", estado_cen)

    if (estado != ESTADO_RECONOCIMIENTO and
        estado != ESTADO_POST_RECON and
        estado_izq == EXTREMO_LEJANO_AL_LIMITE):
        estadoAnteriorAReconocimiento = estado
        return ESTADO_RECONOCIMIENTO

    if estado == ESTADO_RECONOCIMIENTO:
        print("\t\tCONTADOR: ",contador_ciclos_reconocimiento)

        if contador_ciclos_reconocimiento < len(LISTA_A_RECONOCIMIENTO) -1:
            contador_ciclos_reconocimiento += 1
            distanciasReconocimiento.append(data[IZQ])
            return estado
        else:
            contador_ciclos_reconocimiento = 0
            print("\n\nSE ACABARON LOS CICLOS DE RECONOCIMIENTO\n")
            minima_dist = min(distanciasReconocimiento)
            print("Minimima dist: ", minima_dist, "\t lista dist: ", distanciasReconocimiento)
            posicionDistanciaElegidaRec = distanciasReconocimiento.index(minima_dist)
            print("++++++++++POSICION: ", posicionDistanciaElegidaRec)
            return ESTADO_POST_RECON #Si se acaban los ciclos de recon sin encontrar nada, gira la pared
    
    elif estado == ESTADO_POST_RECON:
        if contador_ciclos_reconocimiento < posicionDistanciaElegidaRec:
            contador_ciclos_reconocimiento = contador_ciclos_reconocimiento + 1
            return estado
        else:
            contador_ciclos_reconocimiento = 0
            posicionDistanciaElegidaRec = -1
            distanciasReconocimiento = []
            return estadoAnteriorAReconocimiento

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
        elif estado_izq == INFERIOR_AL_LIMITE or estado_izq == EXTREMO_CERCANO_PARED:
            return ESTADO_CORREGIR_DER
        elif estado_izq == SUPERIOR_AL_LIMITE:
            return ESTADO_CORREGIR_IZQ

    elif estado == ESTADO_CORREGIR_IZQ:
        if estado_izq == CENTRADO_ENTRE_LIMITES:
            if isOrigenAvanzar:
                return ESTADO_AVANZAR
            else:
                return ESTADO_EMPUJAR
        elif estado_izq == INFERIOR_AL_LIMITE or estado_izq == EXTREMO_CERCANO_PARED:
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
        if estado_izq == EXTREMO_CERCANO_PARED:
            return ESTADO_PRE_GIRO

    elif estado == ESTADO_PRE_GIRO:
        if estado_cen == INFERIOR_AL_LIMITE:
            return ESTADO_GIRO_DER
        
    elif estado == ESTADO_GIRO_DER:
            return ESTADO_EMPUJAR
    
    elif estado == ESTADO_EMPUJAR:
        isOrigenAvanzar = False
        if estado_cen == INFERIOR_AL_LIMITE:
            return ESTADO_GIRO_BOLAS
        elif estado_izq == EXTREMO_CERCANO_PARED:
            return ESTADO_CORREGIR_DER
        elif estado_izq == SUPERIOR_AL_LIMITE:
            return ESTADO_CORREGIR_IZQ
    
    elif estado == ESTADO_GIRO_BOLAS:
        return ESTADO_AVANZAR


    return estado


def main():
    #Se declara el subscriber de los ultrasonidos
    rospy.Subscriber('Ultrasonidos_data', Int16MultiArray, subsUltrasonidos)
    # Estado en el que se encuentra el robot
    estado = ESTADO_INDETERMINADO 

    global data, dist_pared_inicial
    global limites_inf, limites_sup, MAX_LIMITE_EXTREMO
    
    while dist_pared_inicial == INDETERMINADO:
        if len(data):
            data_fija = data
            print("DAFIJA: ", data_fija)
            dist_pared_inicial = data_fija[IZQ]
    
    limites_inf = [max([dist_pared_inicial-5, 15]),20,15] #FIXME
    limites_sup = [limites_inf[IZQ] + 10, 40, dist_pared_inicial + 10]

    
    MAX_LIMITE_EXTREMO = [max([40, limites_sup[IZQ]]), 9999999, 99999999]



    print("\n\n------------------LIMITE MIN: ", MIN_LIMITE_EXTREMO)
    print("\n\n------------------LIMITE inferior: ", limites_inf)
    print("\n\n------------------LIMITE SUPERIOR: ", limites_sup)
    print("\n\n------------------LIMITE EXTREMO: ", MAX_LIMITE_EXTREMO)
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