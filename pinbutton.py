#--------------------------------------------------------------------
#author	: N.Pronk
#date	: jan 2023
#licence: published under MIT licence
#
#Description
#--------------------------------------------------------------------
#Wrapper for pin 
#--------------------------------------------------------------------
from machine import Pin
from debugableitem import DebugableItem

class PinButton(DebugableItem):
    onclicked=None
    ondoubleclicked=None
    ondoubleclickcountdown=None
    countdownperiodms = 500
    dblclickcountdownfrom = 1
    
    pin: Pin=None
    def __init__(self, pin: Pin, onclicked, ondoubleclicked, ondoubleclickcountdown, countdownperiodms: int, dblclickcountdownfrom: int):
        """
        @pin: Pin instance - irq based
        #onclicked: function that has to be executed as a single click
        @ondoubleclicked: function that has to be executed on double click
        @ondoubleclickcountdown: function that has to be executed on countdown
        @countdownperiodms: period in milliseconds between two counts
        @dblclickcountdownfrom: countdown to start from
        """
        self.pin=pin
        self.onclicked=onclicked
        self.ondoubleclicked=ondoubleclicked
        self.ondoubleclickcountdown=ondoubleclickcountdown
        if (countdownperiodms > 0):
            self.countdownperiodms = countdownperiodms
        if (dblclickcountdownfrom > 0):
            self.dblclickcountdownfrom = dblclickcountdownfrom