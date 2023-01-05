#--
#author	: N.Pronk
#date	: jan 2023
#licence: published under MIT licence
#
#Description
#--
#Example program for debouncing and countdown for pin-buttons
#--

from machine import Pin
from simpledebugger import SimpleDebugger
from pinmonitor import PinMonitor
from pinbutton import PinButton

dbg=SimpleDebugger()
dbg.dbg_out('Start dbg')

#define some functions - later on used in buttons
def pin18clicked(pinbutton: PinButton):
    print(">>>>>>>> pin18clicked", pinbutton )

def pin18doubleclicked(pinbutton: PinButton):
    print(">>>>>>>> pin18doubleclicked", pinbutton )
    
def pin18ondoubleclickcountdown(pinbutton: PinButton):
    print(">>>>>>>> pin18ondoubleclickcountdown", pinbutton, pinbutton.countdownvalue)

def pin19clicked(pinbutton: PinButton):
    if pinbutton.countdownvalue>0:
        print(">>>>>>>> Self destruct NCC-1701 started...Kahn is about to start his last attack on the crappy Enterprise ", pinbutton, pinbutton.countdownvalue)
    else:
        print(">>>>>>>> Life goes on. We remember the Enterprise NCC-1701.", pinbutton, pinbutton.countdownvalue )

def pin19doubleclicked(pinbutton: PinButton):
    print(">>>>>>>> Self destruct NCC-1701 disabled..Enterprise flies. Kahn is dead. Kirk is happy. Spock still does not smile ", pinbutton, pinbutton.countdownvalue)

def pin19ondoubleclickcountdown(pinbutton: PinButton):
    if (pinbutton.countdownvalue >0):
        print(">>>>>>>> selfdestruct NCC-1701 active.....Countdown to destruction" , pinbutton.countdownvalue)
    elif (pinbutton.countdownvalue == 0):
        print(">>>>>>>> Enterprise NCC-1701 exploded.....Kirk and Spock transported in time to the planet", pinbutton, pinbutton.countdownvalue )

#create the pin monitor that monitors the behaviour of the buttons
dbg.dbg_enter("create pinmonitor")
pinmon1=PinMonitor()
pinmon1.debugger=dbg
pinmon1.debug=True


dbg.debug=True
dbg.dbg_enter("create pinmonitor")

dbg.dbg_enter("register pinbuttons")

#register a button with 'normal' behaviour 
pinmon1.registerpinbutton(PinButton(Pin(18, Pin.IN, Pin.PULL_DOWN), pin18clicked, pin18doubleclicked,pin18ondoubleclickcountdown, 0, 0))

#register a button with a click at start and click after 10 seconds (10*1000ms) and a countdown interval of 1 sec
#unless the user presses the button within the 10 secs. When the user does that the pin19doubleclicked function will be executed.
#On countdown the pin19ondoubleclickdecount function will be executed
#Most likely usage is a self destruct button (self destruct in 10 seconds)
pinmon1.registerpinbutton(PinButton(Pin(19, Pin.IN, Pin.PULL_DOWN), pin19clicked, pin19doubleclicked,pin19ondoubleclickcountdown, 1000, 10 ))
dbg.dbg_leave("register pinbuttons")

print("\r\nPress the buttons attached to the pins and see what happens\r\n")


