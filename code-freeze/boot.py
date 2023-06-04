# reorganize search path - .frozen last!
import sys
sys.path.remove('.frozen')
sys.path.extend(['webserver', 'adafruit', '.frozen'])
