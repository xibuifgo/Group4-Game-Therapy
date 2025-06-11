import serial
import serial.tools.list_ports

ports = serial.tools.list_ports.comports(include_links=True)
available = [port.device for port in ports]

names = [port.vid for port in ports]

print(available)
print(names)