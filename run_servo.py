import time
import RPi.GPIO as GPIO
from system.active_components import Servo

GPIO.setmode(GPIO.BCM)

if __name__ == '__main__':
    s = Servo(13, 0.5 / 20 * 100, 1.5 / 20 * 100)
    angle45 = 45.0
    angle90 = 90.0
    angle00 = 0.0

    # pwm = s.get_angle_pwm(angle)
    # print(f"Setting servo to angle: {angle} with a pwm duty of {pwm}")

    s.rotate_to_angle(angle00)
    time.sleep(0.5)

    s.rotate_to_angle(angle45)
    time.sleep(0.5)

    s.rotate_to_angle(angle00)
    time.sleep(0.5)

    s.rotate_to_angle(angle90)
    time.sleep(0.5)

    # s.sin_response(100, 0.2)

    time.sleep(0.5)
    s.stop()

    GPIO.cleanup()
