from system.main_system import System
from data_handling.custom_logger import create_system_logger 

if __name__ == "__main__":
    sl = create_system_logger()
    
    sl.info("test ONE")
    
    s = System()
    s.enter_main_loop()    
