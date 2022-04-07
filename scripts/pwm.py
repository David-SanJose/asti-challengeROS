import RPi.GPIO as GPIO
import time
from time import sleep

GPIO.setmode(GPIO.BOARD)

MotorIN1 = 36
MotorIN2 = 22
MotorE1 = 12

GPIO.setup(MotorIN1,GPIO.OUT)
GPIO.setup(MotorIN2,GPIO.OUT)
GPIO.setup(MotorE1,GPIO.OUT)

p = GPIO.PWM(MotorE1, 50)  # Creamos la instancia PWM con el GPIO a utilizar y la frecuencia de la señal PWM
p.start(0)  #Inicializamos el objeto PWM

print("Hacemos girar el motor en un sentido por 10 segundos mientras aumentamos  y disminuimos la velocidad")
GPIO.output(MotorIN1,GPIO.HIGH) # Establecemos el sentido de giro con los pines IN1 e IN2  
GPIO.output(MotorIN2,GPIO.LOW)  # Establecemos el sentido de giro con los pines IN1 e IN2

for dc in range(33, 101, 1):
    p.ChangeDutyCycle(dc)
    time.sleep(0.05)

for dc in range(100, -1, -1):
    p.ChangeDutyCycle(dc)
    time.sleep(0.05)

print("Hacemos girar el motor en el sentido contrario por 10 segundos mientras aumentamos  y disminuimos la velocidad")
GPIO.output(MotorIN1,GPIO.LOW) # Establecemos el sentido de giro con los pines IN1 e IN2  
GPIO.output(MotorIN2,GPIO.HIGH)  # Establecemos el sentido de giro con los pines IN1 e IN2

for dc in range(33, 101, 1):
    p.ChangeDutyCycle(dc)
    time.sleep(0.05)

for dc in range(100, -1, -1):
    p.ChangeDutyCycle(dc)
    time.sleep(0.05)

print ("Detenemos el motor")
p.ChangeDutyCycle(0)
sleep(1)

GPIO.cleanup()
