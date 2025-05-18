import serial
import serial.tools.list_ports
import threading


class SerialManager:
    _instance = None

    def __new__(cls):
        """Ensure only one instance exists (Singleton pattern)."""
        if cls._instance is None:
            cls._instance = super(SerialManager, cls).__new__(cls)
            cls._instance.serial_port = None  # Placeholder for detected port
            cls._instance.data = None  # Shared variable for storing data
            cls._instance.running = False  # Flag to control reading thread
            cls._instance.data_log = []  # Store received data
            cls._instance.detect_serial_port()  # Auto-detect and connect
        return cls._instance

    def detect_serial_port(self):
        """Scan available ports and connect to a valid one."""
        available_ports = list(serial.tools.list_ports.comports())
        
        for port_info in available_ports:
            port_name = port_info.device
            for baudrate in [9600, 115200, 57600, 38400, 19200]:  # Common baud rates
                try:
                    ser = serial.Serial(port_name, baudrate, timeout=1)
                    if ser.is_open:
                        print(f"Connected to {port_name} at {baudrate} baud")
                        self.serial_port = ser
                        self.running = True
                        self.start_reading()
                        return  # Exit once a valid connection is found
                except serial.SerialException:
                    continue  # Try the next baud rate

        print("No valid serial port detected.")

    def start_reading(self):
        """Start a background thread for reading data asynchronously."""
        if self.serial_port:
            thread = threading.Thread(target=self.read_data, daemon=True)
            thread.start()

    def read_data(self):
        """Continuously read data and store it in a shared variable."""
        while self.running:
            if self.serial_port.in_waiting:
                self.data = self.serial_port.readline().decode('utf-8').strip()
                self.data_log.append(self.data)  # Save data for logging
                
                

    def get_latest_data(self):
        """Return the most recent data received."""
        return self.data

    def get_logged_data(self):
        """Return all stored data."""
        return self.data_log

    def stop(self):
        """Close the serial connection gracefully."""
        self.running = False
        if self.serial_port:
            self.serial_port.close()
            print("Serial connection closed.")

# Example Usage
if __name__ == "__main__":
    serial_manager = SerialManager()
    
    import time
    time.sleep(2)  # Wait to collect some data

    print("Latest Data:", serial_manager.get_latest_data())
    print("Logged Data:", serial_manager.get_logged_data())

    serial_manager.stop()  # Stop reading safely