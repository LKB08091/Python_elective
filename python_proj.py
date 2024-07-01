import RPi.GPIO as GPIO
import sys
import spidev
import time
import datetime
import requests
import json
from mfrc522 import SimpleMFRC522
import dht11
import I2C_LCD_driver
import threading
import requests

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(24,GPIO.OUT) #LED, set GPIO 24 as output
GPIO.setup(18,GPIO.OUT) #buzzer, set GPIO 18 as output
buzzer_pwm = GPIO.PWM(18,100)
#set 100Hz PWM output at GPIO 18 (buzzer)
#use PWM.start(1) to activate
GPIO.setup(23, GPIO.OUT) #dc motor
motor_pwm=GPIO.PWM(23,50) #motor pwm freq is 50hz
GPIO.setup(25,GPIO.OUT) #GPIO25 as Trig
GPIO.setup(27,GPIO.IN) #GPIO27 as Echo

Token = ""
chat_id=''
message=""

#keypad
matrix=[[1,2,3],[4,5,6],[7,8,9],["*",0,"#"]]
row=[6,20,19,13]
col=[12,5,16]
#set column pins as outputs, and write default value of 1 to each
for i in range(3):
    GPIO.setup(col[i],GPIO.OUT)
    GPIO.output(col[i],1)
#set row pins as inputs, with pull up
for j in range(4):
    GPIO.setup(row[j],GPIO.IN,pull_up_down=GPIO.PUD_UP)

LCD = I2C_LCD_driver.lcd() #instantiate an lcd object, call it LCD
LCD.backlight(1)


class products():
    def __init__(self,name,id,price,quantity):
        self.name=name
        self.id=id
        self.price=price
        self.quantity=quantity

#init some products objects
Product1=products("Panadol with Optizorb Caplets",1,7.9,5)
Product2=products("Hansaplast Plasters",2,2.7,4)
Product3=products("Whisper Wings Pads",3,6.2,3)
        
#then store in a dictionary to loop during product selection
product_list={
    Product1.id: Product1,
    Product2.id: Product2,
    Product3.id: Product3
    }

product_quantity={
    Product1.quantity:Product1,
    Product2.quantity:Product2,
    Product3.quantity:Product3
    }


def display_item_price(item_id):
    #led display the price of products selected
    item=product_list.get(item_id)
    if item & item.quantity>0:
        return item.price
    #if product that is not available is selected, display not available
    else:
        return "Not available"
    
def change_item_count(item_id):
    item=product_quantity.get(item_id)
    if item:
        item.quantity=item.quantity-1
        return 
    else:
        return "Not available"

#def payment():
    #make sure payment is made
    #read rfid card asnd deduct amount that is stored on a remote site


def dispense(duration):
    #turn motor a certain way to dispense the product
    #m=20 or any number)
    #my_pwm.start(m)
    motor_pwm.start(duration)

#def send_data():
    #send data to ThingSpeak

def ultrasound():
    #produce a 10us pulse at Trig
    GPIO.output(25,1) 
    time.sleep(0.00001)
    GPIO.output(25,0)

    #measure pulse width (i.e. time of flight) at Echo
    StartTime=time.time()
    StopTime=time.time()
    while GPIO.input(27)==0:
        StartTime=time.time() #capture start of high pulse       
    while GPIO.input(27)==1:
        StopTime=time.time() #capture end of high pulse
    ElapsedTime=StopTime-StartTime

    #compute distance in cm, from time of flight
    Distance=(ElapsedTime*34300)/2
       #distance=time*speed of ultrasound,
       #/2 because to & fro
    return Distance

def dht11():
    try:
        while True: #keep reading, unless keyboard is pressed
            result = instance.read()
        if result.is_valid(): #print datetime & sensor values
            print("Last valid input: " +     
                str(datetime.datetime.now()))
            print("Temperature: %-3.1f C" % result.temperature)
            print("Humidity: %-3.1f %%" % result.humidity)
        time.sleep(0.5) #short delay between reads

    except KeyboardInterrupt:
        print("Cleanup")
        GPIO.cleanup() #Google what this means…
    

def keypad():
    #scan keypad
    while (True):
        for i in range(3): #loop thru’ all columns
            GPIO.output(COL[i],0) #pull one column pin low
            for j in range(4): #check which row pin becomes low
                if GPIO.input(ROW[j])==0: #if a key is pressed
                    print (MATRIX[j][i]) #print the key pressed
                    key_pressed=MATRIX[j][i]
                    while GPIO.input(ROW[j])==0: #debounce
                        sleep(0.1)
                    return key_pressed
            GPIO.output(COL[i],1) #write back default value of 1

def lcd(content,line):
    LCD.backlight(1) #turn backlight on 
    #LCD.lcd_display_string("LCD Display Test", 1) #write on line 1
    #LCD.lcd_display_string("Address = 0x27", 2, 2) #write on line 2
              #starting on 3rd column
    LCD.lcd_display_string(content, line)
    LCD.lcd_clear() #clear the display



#main function
#ultrasound detect for customer
distance=ultrasound()
while True:
    #lcd display welcome, keeps checking for customers
    if distance > 10:
        distance=ultrasound()
        lcd("Welcome!",1)
    else:
    #customer is detected
        lcd("Medicine Vending Machine",1)
        lcd("Please select an item", 2)
    #check what button customer presses
        key_pressed=keypad()
    #find the product coresponding to key_pressed
        price=display_item_price(key_pressed)
    #display price on lcd
        lcd(str(price),1)
    #check if customer pays
    #deduct amount from cust account
    #change item count
        change_item_count(key_pressed)
    #LED is green
        GPIO.output(24,1)
    #LCD display successful
        lcd("Thank you,1")
    #motor turns
        dispense(3)


"""while True:
    # create threads
    #change to main function and web server
    thread1 = threading.Thread(target=keypad_scan)
    thread3 = threading.Thread(target=message_check)

    # start threads
    thread1.start()
    thread3.start()

    if activate_ultrasound:
        thread2 = threading.Thread(target=ultrasound_scan)
        thread2.start()
        thread2.join()

    # wait for threads to finish
    thread1.join()
    thread3.join()
"""
