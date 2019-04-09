from system.project_system import System
from data_handling.custom_logger import create_system_logger

if __name__ == "__main__":
    # Crate a logger for main running operation
    sl = create_system_logger()

    # Setup the system
    s = System(default_enabled=True)

    # Accept keyboard interrupts
    try:
        s.enter_main_loop()
    except KeyboardInterrupt:
        sl.info("System shutting down. Goodbye cruel world.")
