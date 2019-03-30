import time
import RPi.GPIO as GPIO
from system.active_components import Servo

from system import system_constants



#GPIO.cleanup()


GPIO.setmode(GPIO.BCM)

if __name__ == '__main__':
    
    servo_number = 0
    
    servo_pin = system_constants.room_servo_pins[servo_number]
    
    duty_deg_0, duty_deg_90, = system_constants.servo_duty_calibrations[servo_number]
    
    s = Servo(servo_pin, duty_deg_0, duty_deg_90)
    angle45 = 45.0
    angle90 = 90.0
    angle00 = 0.0


    try:
        while True:
            #try:
                
            cmd = input("Enter a command: ")
            
            cmd_args = cmd.split()
            
            if cmd_args[0] == "a":
                angle = float(cmd_args[1]) 
                pwm = s.get_angle_pwm(angle)
                print(f"Setting servo to angle: {angle} with a pwm duty of {pwm}")
                s.apply_duty(pwm)
                
            if cmd_args[0] == "d":
                
                pwm = float(cmd_args[1]) 
                print(f"Setting servo to pwm duty of {pwm}")
                s.apply_duty(pwm)
    except KeyboardInterrupt:
           pass 

    #s.rotate_to_angle(angle00)
    #time.sleep(0.5)

    #s.rotate_to_angle(angle45)
    #time.sleep(0.5)

    #s.rotate_to_angle(angle00)
    #time.sleep(0.5)

    #s.rotate_to_angle(angle90)
    #time.sleep(0.5)

    # s.sin_response(100, 0.2)

    #time.sleep(0.5)
    s.stop()

    GPIO.cleanup()
