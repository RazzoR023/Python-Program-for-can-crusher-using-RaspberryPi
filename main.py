import  RPi.GPIO as GPIO
import  time
import  zbar
from SimpleCV  import  Color,Camera
import  MySQLdb

timeout_start = time.time()  # Usage of 'time' module to automate the program waiting time.
timeout = 3
can_count = 0

def qread():  # Function to scan QR code and read the data in it
    cam = Camera()  
    count = 0
    timeout_st = time.time()
    timout = 7
    result = None
    while(count < 1 and time.time() < timeout_st + timout):
        
        img = cam.getImage()
        barcode = img.findBarcode()
        if(barcode is not None):
            barcode = barcode[0] 
            result = str(barcode.data)
            
            barcode = [] 
            count = 1
    del cam
    return result 

def write(name, can_count):  # Function to write in MySQLdatabase
    db = MySQLdb.connect("localhost", "monitor", "pasword", "qr") # Pre-Existing Database details
    curs=db.cursor()
    try:
        curs.execute ("INSERT INTO reward(name, count) VALUES(%s, %s) ON DUPLICATE KEY UPDATE count = count + VALUES(count)",(name, int(can_count)))
        db.commit()
        
    except:
        print "error"
        db.rollback()

while 1:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(17, GPIO.OUT) # Initial pin configuration
    GPIO.setup(23, GPIO.IN)
    GPIO.output(17, GPIO.LOW)
    timeout_start = time.time()
    while time.time() < timeout_start + timeout: # This control statement run the following code for the given amount of time
        if (GPIO.input(23) == 1): # This input will be low if a object is detected via Infared sensor
            GPIO.output(17, GPIO.LOW)
            print "no object" # print statements used for identifying program control line
            time.sleep(1)
            
        else:
            GPIO.output(17, GPIO.HIGH)
            print "light"
            timeout_start = time.time()
            can_count +=1
            print can_count
            time.sleep(5)
            GPIO.output(17, GPIO.LOW) # Since Object is detected & counted, this step allows for a pneumatic cyclinder to crush the object ie. a tin can
            time.sleep(2.5)           # Calculated time required for single stroke from the crusher
            timeout_start = time.time()
    
    print "out of loop"
    if can_count == 0:
        continue
    elif can_count > 0:
        name = None
        name = qread()  # Reading QR code if there is a count
        if (name != None):
            write(name, can_count)
            print "write commited"
    can_count = 0
    timeout_start = time.time()
    GPIO.cleanup()
