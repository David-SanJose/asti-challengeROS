from hardware.Sensores_ldr import talker
import rospy
from std_msgs.msg import String

''' LDRs
LDRFL = 19  Frontal Izquierdo 0
LDRFR = 22  Frontal Derecho 1

LDRrightF = 21  Derecho superior 2
LDRrightB = 24  Derecho inferior 3

LDRBL = 23  Trasero Izquierdo 4
LDRBR = 26  Trasero Derecho 5

LDRleftF = 38  Izquierdo superior 6
LDRleftB = 40  Izquierdo  7
'''

''' Direcciones
 0  1 derecha
 0 -1 izquierda
 1  0 abajo
-1  0 arriba
'''
class Sigue_lineas:
    def __init__(self, array_direcciones):
        self.array_direcciones = array_direcciones
        self.cruces_pasados = 0
        self.contador_cruce = 0
        self.contador_desviacion_d = 0 # desviacion a la derecha
        self.contador_desviacion_a = 0 # desviacion a la izq
        self.contador_desviacion_w = 0 # desviacion hacia arriba
        self.contador_desviacion_s = 0 # desviacion hacia abajo
        self.ultimo_movimiento = ''
        self.ultima_correccion = '' # de momento no la uso
        self.contador_prueba = 0
        self.seguir = True
        self.listener()

    def traducir_movimiento(self, direccion : str):
        if direccion == '01':
            return 'd'
        elif direccion == '0-1':
            return 'a'
        elif direccion == '10':
            return 's'
        elif direccion == '-10':
            return 'w'
    
    def calcular(self, data):
        while len(self.array_direcciones) > self.cruces_pasados:
            # si todo está blanco avanzar
            if data.data.count(0) == 8:
                if self.ultimo_movimiento == '':
                    self.ultimo_movimiento = self.traducir_movimiento(self.array_direcciones[0])
                talker(self.ultimo_movimiento)
                self.contador_desviacion_d = 0
                self.contador_desviacion_a = 0

            # si hay algun sensor que detecta negro, analizar la situación
            if data.data[0] == 1 and data.data[5] == 1: # desvio a la derecha
                talker('a')
                self.ultima_correccion = 'a'
            if data.data[1] == 1 and data.data[4] == 1: # desvio a la izquierda
                talker('d')
                self.ultima_correccion = 'd'
            if data.data[2] == 1 and data.data[7] == 1: # desvio hacia abajo
                talker('w')
                self.ultima_correccion = 'w'
            if data.data[3] == 1 and data.data[6] == 1: # desvio hacia arriba
                talker('s')
                self.ultima_correccion = 's'

            if data.data[0] == 1:
                self.contador_desviacion_a +=1
    
    def calcular_de_prueba(self, data):
        en_mov = False
        if data.data[0] == 0 and data.data[1] == 0 and data.data[2] == 0 and data.data[5] == 0:
            if self.contador_prueba <=10: # esto es para esperar al menos 1 tick antes de parar
                if not en_mov and self.seguir == True:
                    talker('w')
                    en_mov = True
            else:
                talker('f')
                en_mov = False
                self.seguir = False
            
        elif data.data[0] == 1 and data.data[1] == 1:
            self.contador_prueba += 1
        
        elif data.data[0] == 1 and data.data[5] == 1:
            talker('f')
            talker('a')
            en_mov = True
        elif data.data[1] == 1 and data.data[2] == 2:
            talker('f')
            talker('d')
            en_mov = True
        pass



    '''
    Los string usados para los datos son: 
    "w" hacia delante
    "a" hacia la izquierda
    "s" hacia atras
    "d" hacia la derecha
    "q" pivote hacia la izquierda
    "e" pivote hacia la derecha
    "f" parar
    '''
    def talker(self, processed_data):
        pub = rospy.Publisher('movimiento', String, queue_size = 10)
        rate = rospy.Rate(10) #10hz
        if processed_data == None or processed_data == '' or processed_data == ' ':
            data = 'f'
        else:
            data = processed_data
        while not rospy.is_shutdown():
            pub.publish(data)
            rate.sleep()

    def callback(self, data):
        rospy.loginfo(rospy.get_caller_id() + 'I heard %s', data.data)
        # FIXME aqui va calcular(data)
        self.calcular_de_prueba(data)
        
    def listener(self):
        rospy.init_node('cuadricula', anonymous = True)
        rospy.Subscriber('color_ldr', String, self.callback)
        rospy.spin()

sg = Sigue_lineas([1,2])
sg.calcular_de_prueba()
