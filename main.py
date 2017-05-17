import  RPi.GPIO as GPIO
import  time
import  zbar
from SimpleCV  import  Color,Camera
import  MySQLdb

timeout_start = time.time()
timeout = 3
count = 0

def qread():
    cam = Camera()  
    counti = 0
    timeout_st = time.time()
    timout = 7
    result = None
    while(counti < 1 and time.time() < timeout_st + timout):
        
        img = cam.getImage()
        barcode = img.findBarcode()
        if(barcode is not None):
            barcode = barcode[0] 
            result = str(barcode.data)
            
            barcode = [] 
            counti = 1
    del cam
    return result 

def write(name, count):
    db = MySQLdb.connect("localhost", "monitor", "pasword", "qr")
    curs=db.cursor()
    try:
        curs.execute ("INSERT INTO reward(name, count) VALUES(%s, %s) ON DUPLICATE KEY UPDATE count = count + VALUES(count)",(name, int(count)))
        db.commit()
        
    except:
        print "error"
        db.rollback()

while 1:
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(17, GPIO.OUT)
    GPIO.setup(23, GPIO.IN)
    GPIO.output(17, GPIO.LOW)
    timeout_start = time.time()
    while time.time() < timeout_start + timeout:
        if (GPIO.input(23) == 1):
            GPIO.output(17, GPIO.LOW)
            print "no object"
            time.sleep(1)
            
        else:
            GPIO.output(17, GPIO.HIGH)
            print "light"
            timeout_start = time.time()
            count +=1
            print count
            time.sleep(5)
            GPIO.output(17, GPIO.LOW)
            time.sleep(2.5)
            timeout_start = time.time()
    
    print "out of loop"
    if count == 0:
        continue
    elif count > 0:
        name = None
        name = qread()
        if (name != None):
            write(name, count)
            print "write commited"
    count = 0
    timeout_start = time.time()
    GPIO.cleanup()
