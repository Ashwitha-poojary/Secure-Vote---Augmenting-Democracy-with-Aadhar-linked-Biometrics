import serial
import re
import time

port = 'COM8'
def collet(id):
    try:
        ser = serial.Serial(port=port,baudrate=9600,timeout=5)  # open serial port
               

        if ser.isOpen():
            print("Serial port is open.")
        else:
            print("Failed to open serial port.")
            return False

        while True:
            # print("Reading port....")
           
            ser.write(b"a")
            # time.sleep(3)
            data = ser.readline().decode().rstrip()
            print(data)
            
            if data.startswith("Stored!"):
                ser.close()
                print("Serial port closed.")
                return True  
                
            ser.write(id.encode())
            # time.sleep(3)
            data = ser.readline().decode().rstrip()
            print(data)
        

    except KeyboardInterrupt:
        # Clean up the serial port when the script is interrupted
        ser.close()
        print("Serial port closed.")
        return False

    return False


def search():
    try:
        ser = serial.Serial(port=port,baudrate=9600,timeout=5)  # open serial port
               

        if ser.isOpen():
            print("Serial port is open.")
        else:
            print("Failed to open serial port.")
            return None

        while True:
            # print("Reading port....")
           
            ser.write(b"s")
            time.sleep(5)
            data = ser.readline().decode('utf-8').strip()
            print(data)
            if data.startswith("$"):
                ser.close()
                print("Serial port closed.")
                return data  
            # ser.close()
            # print("Serial port closed.")
            # return data  
            
        

    except KeyboardInterrupt:
        # Clean up the serial port when the script is interrupted
        ser.close()
        print("Serial port closed.")
        return None

    return None




