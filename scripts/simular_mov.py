import RPi.GPIO as GPIO
import time
import threading
from time import sleep

GPIO.cleanup()
GPIO.setmode(GPIO.BOARD)

# LDRs
LDRFL = 19 #LDR 31 FI
LDRFR = 22 #LDR 10 DF

LDRleft = 21 #LDR 7I
LDRright = 24 #LDR 8D

LDRBL = 23 #LDR 29 BI
LDRBR = 26 #LDR 11 BD


# A y B para la polaridad (giro de las ruedas)
MotorE1 = 12 # Enable de los motores

Motor0A=16
Motor0B=18

Motor1A=3
Motor1B=5

Motor2A=7
Motor2B=11

Motor3A=13
Motor3B=15

GPIO.setup(LDRFL,GPIO.IN)
GPIO.setup(LDRFR,GPIO.IN)
GPIO.setup(LDRleft,GPIO.IN)
GPIO.setup(LDRright,GPIO.IN)
GPIO.setup(LDRBL,GPIO.IN)
GPIO.setup(LDRBR,GPIO.IN)

GPIO.setup(Motor0A,GPIO.OUT)
GPIO.setup(Motor0B,GPIO.OUT)

GPIO.setup(Motor1A,GPIO.OUT)
GPIO.setup(Motor1B,GPIO.OUT)

GPIO.setup(Motor2A,GPIO.OUT)
GPIO.setup(Motor2B,GPIO.OUT)

GPIO.setup(Motor3A,GPIO.OUT)
GPIO.setup(Motor3B,GPIO.OUT)

def Forward():

    GPIO.output(Motor0A,GPIO.LOW)
    GPIO.output(Motor0B,GPIO.HIGH) 
    GPIO.output(Motor1A,GPIO.HIGH)
    GPIO.output(Motor1B,GPIO.LOW) 
    GPIO.output(Motor2B,GPIO.LOW)
    GPIO.output(Motor2A,GPIO.HIGH) 
    GPIO.output(Motor3B,GPIO.LOW)
    GPIO.output(Motor3A,GPIO.HIGH)

    
def Back():

    GPIO.output(Motor0A,GPIO.HIGH)
    GPIO.output(Motor0B,GPIO.LOW) 
    GPIO.output(Motor1B,GPIO.HIGH)
    GPIO.output(Motor1A,GPIO.LOW) 
    GPIO.output(Motor2A,GPIO.LOW)
    GPIO.output(Motor2B,GPIO.HIGH) 
    GPIO.output(Motor3A,GPIO.LOW)
    GPIO.output(Motor3B,GPIO.HIGH)



def Left():
    GPIO.output(Motor0A,GPIO.HIGH)
    GPIO.output(Motor0B,GPIO.LOW) 
    GPIO.output(Motor1A,GPIO.HIGH)
    GPIO.output(Motor1B,GPIO.LOW) 
    GPIO.output(Motor2B,GPIO.LOW)
    GPIO.output(Motor2A,GPIO.HIGH)  
    GPIO.output(Motor3B,GPIO.HIGH)
    GPIO.output(Motor3A,GPIO.LOW) 



def Right():
    GPIO.output(Motor0B,GPIO.HIGH)
    GPIO.output(Motor0A,GPIO.LOW) 
    GPIO.output(Motor1B,GPIO.HIGH)
    GPIO.output(Motor1A,GPIO.LOW) 
    GPIO.output(Motor2B,GPIO.HIGH)
    GPIO.output(Motor2A,GPIO.LOW)  
    GPIO.output(Motor3A,GPIO.HIGH)
    GPIO.output(Motor3B,GPIO.LOW) 


def TurnR():
    GPIO.output(Motor0B,GPIO.HIGH)
    GPIO.output(Motor0A,GPIO.LOW) 
    GPIO.output(Motor1B,GPIO.HIGH)
    GPIO.output(Motor1A,GPIO.LOW) 
    GPIO.output(Motor2A,GPIO.HIGH)
    GPIO.output(Motor2B,GPIO.LOW) 
    GPIO.output(Motor3A,GPIO.LOW)
    GPIO.output(Motor3B,GPIO.HIGH)




def TurnL():
    GPIO.output(Motor0A,GPIO.HIGH)
    GPIO.output(Motor0B,GPIO.LOW) 
    GPIO.output(Motor1A,GPIO.HIGH)
    GPIO.output(Motor1B,GPIO.LOW) 
    GPIO.output(Motor2B,GPIO.HIGH)
    GPIO.output(Motor2A,GPIO.LOW) 
    GPIO.output(Motor3B,GPIO.LOW)
    GPIO.output(Motor3A,GPIO.HIGH)
    
def Stop():
    GPIO.output(Motor0A,GPIO.LOW)
    GPIO.output(Motor0B,GPIO.LOW) 
    GPIO.output(Motor1A,GPIO.LOW)
    GPIO.output(Motor1B,GPIO.LOW) 
    GPIO.output(Motor2B,GPIO.LOW)
    GPIO.output(Motor2A,GPIO.LOW) 
    GPIO.output(Motor3B,GPIO.LOW)
    GPIO.output(Motor3A,GPIO.LOW)

while True:
    i = input()
    if i == 'w':
        Forward()
        sleep(0.3)
    if i == 'a':
        Left()
        sleep(0.3)
    if i =='d':
        Right()
        sleep(0.3)
    if i =='s':
        Back()
        sleep(0.3)
    if i == 'q':    
        TurnL()
        sleep(0.3)
    if i == 'e':
        TurnR()
        sleep(0.3)
        
    if i == 'f':
        Stop()
        GPIO.cleanup()