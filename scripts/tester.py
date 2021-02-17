hex_string = 'Obala izme\x1au rta \x8ailo i Vodoto\x1a'
print ( hex_string.decode('iso-8859-9'))
print ( hex_string.decode('iso-8859-9').encode('utf-8'))