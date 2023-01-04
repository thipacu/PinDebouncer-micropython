#--------------------------------------------------------------------
#author	: N.Pronk
#date	: jan 2023
#licence: published under MIT licence
#
#Description
#--------------------------------------------------------------------
#Example program for debouncing and countdown for pin-buttons
#--------------------------------------------------------------------

from machine import Pin
from simpledebugger import SimpleDebugger
from pinmonitor import PinMonitor
from pinbutton import PinButton

dbg=SimpleDebugger()
dbg.dbg_out('Start dbg')

#define some functions - later on used in buttons
def pin18clicked(context):
    print("---pin18clicked---", context)

def pin18doubleclicked(context):
    print("---pin18doubleclicked---", context)
    
def pin18ondoubleclickdecount(count):
    print("---pin18ondoubleclickdecount---", count)

def pin19clicked(context):
    global inselfdestruct
    print("---Enterprise exploded. Kirk and Spock transported in time to the planet---", context)

def pin19doubleclicked(context):
    print("---Self destruct disabled. Enterprise flies. Kahn is dead. Kirk is happy. Spock still does not smile ---", context)

def pin19ondoubleclickcountdown(count):
    print("---selfdestruct Enterprise active. Countdown to destruction---", count)

#create the pin monitor that monitors the behaviour of the buttons
dbg.dbg_enter("create pinmonitor")
pinmon1=PinMonitor()
pinmon1.debugger=dbg
pinmon1.debug=True


dbg.debug=False
dbg.dbg_enter("create pinmonitor")

dbg.dbg_enter("register pinbuttons")

#register a button with 'normal' behaviour 
pinmon1.registerpinbutton(PinButton(Pin(18, Pin.IN, Pin.PULL_DOWN), pin18clicked, pin18doubleclicked,pin18ondoubleclickdecount, 0, 0))

#register a button with a click at start and click after 10 seconds (10*1000ms) and a countdown interval of 1 sec
#unless the user presses the button within the 10 secs. When the user does that the pin19doubleclicked function will be executed.
#On countdown the pin19ondoubleclickdecount function will be executed
#Most likely usage is a self destruct button (self destruct in 10 seconds)
pinmon1.registerpinbutton(PinButton(Pin(19, Pin.IN, Pin.PULL_DOWN), pin19clicked, pin19doubleclicked,pin19ondoubleclickcountdown, 1000, 10 ))
dbg.dbg_leave("register pinbuttons")

print("\r\nPress the buttons attached to the pins and see what happens\r\n")


