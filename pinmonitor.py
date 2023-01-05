#--------------------------------------------------------------------
#author	: N.Pronk
#date	: jan 2023
#licence: published under MIT licence
#
#Description
#--------------------------------------------------------------------
#Monitor class for monitor 1 or more buttons based on a pin instance
#with interrupt.
#The main goal is to monitor multiple buttons. Because the number
#of timers is limited a single timer is used for monitoring
#several buttons.
#
#-debounce
#	debounce the interrupts: Ignore interrupt calls during a delay
#
#-doubleclick
#	doubleclick is implemented. Default delay is determined by
#	the pinbutton instance. (500 millisec)
#-countdown
#	Button can be used as a countdown. When the countdown is passed by
#	the singleclick method of the pinbutton will be executed
#
#-keep pressing down - with repeat
#	When holding the button and repeatdelay>0 the singleclick mehod
#	of the pinbutton will be executed after the repeatdelay has passed
#	by
#--------------------------------------------------------------------
import micropython
from machine import Timer
from machine import Pin
import utime
from debugableitem import DebugableItem
from pinbutton import PinButton

#constants
BUTTON_STATE_SINGLECLICK_WAIT=0
BUTTON_STATE_SINGLECLICK_DEBOUNCING=1
BUTTON_STATE_SINGLECLICK_DEBOUNCED=2
BUTTON_STATE_DOUBLECLICK_WAIT=3
BUTTON_STATE_DOUBLECLICK_WAIT_ENDED=4
BUTTON_STATE_DOUBLECLICK_DEBOUNCING=5
BUTTON_STATE_DOUBLECLICK_DEBOUNCED=6
BUTTON_STATE_REPEAT_WAIT=7
BUTTON_STATE_REPEAT_DEBOUNCING=8
BUTTON_STATE_REPEAT_DEBOUNCED=9

class PinMonitor(DebugableItem):
   
    #private    
    _timer=Timer(-1)
    _pinbuttons=[]
    _instance = None
    _activepin= None
    _previouspin = None
    _lastclick_ticks = -1
    _timercallcount=0
    _countdown_maxtimercount=1
    _state=BUTTON_STATE_SINGLECLICK_WAIT
    
    #states as text array because of lack of enums for informational purposes
    _states=[ \
        "BUTTON_STATE_SINGLECLICK_WAIT" \
        , "BUTTON_STATE_SINGLECLICK_DEBOUNCING" \
        , "BUTTON_STATE_SINGLECLICK_DEBOUNCED" \
        , "BUTTON_STATE_DOUBLECLICK_WAIT" \
        , "BUTTON_STATE_DOUBLECLICK_WAIT_ENDED" \
        , "BUTTON_STATE_DOUBLECLICK_DEBOUNCING" \
        , "BUTTON_STATE_DOUBLECLICK_DEBOUNCED" \
        , "BUTTON_STATE_REPEAT_WAIT" \
        , "BUTTON_STATE_REPEAT_DEBOUNCING" \
        , "BUTTON_STATE_REPEAT_DEBOUNCED" \
        ]
    
    #delay=200
    #repeatdelay=100
    
#	 implement new to use as singleton   
#    def __new__(self):
#        if self._instance is None:
#            self._instance = super(PinMonitor, self).__new__(self)
#            # Put any initialization here.
#        return self._instance
    
    def registerpinbutton(self, pinbutton: PinButton):
        self.dbg_enter("{:<25}".format("registerpin"))
        self._pinbuttons.append(pinbutton)
        pinbutton.pin.irq(handler=self._process_state, trigger=Pin.IRQ_RISING)
        self._active_pinbutton=pinbutton
        self._previous_pinbutton=pinbutton
        self.dbg_leave("{:<25}".format("registerpin"))
            
    def unregisterpin(self, pinbutton: PinButton):
        self._reset()
        self._pinbuttons.remove(pinbutton)
        founditem.pin.irq(handler=None, trigger=Pin.IRQ_RISING)
        if self._active_pinbutton==pinbutton:
            self._active_pinbutton=None
        if self._previous_pinbutton==pinbutton:
            self._previous_pinbutton=None

    def _process_state(self,irqflags):
        self.dbg_enter("{:<25}".format("process_state"),self._states[self._state],irqflags,self._active_pinbutton,self._active_pinbutton.pin.value())
        if irqflags!=None:
            self._previous_pinbutton=self._active_pinbutton
            self._active_pinbutton=next((x for x in self._pinbuttons if x.pin==irqflags ))
            if self._previous_pinbutton!=self._active_pinbutton:
                self._timer.deinit()
                self._state=BUTTON_STATE_SINGLECLICK_WAIT
        
        if self._state==BUTTON_STATE_SINGLECLICK_WAIT:
            self._active_pinbutton.countdownvalue=0
            if self._active_pinbutton.dblclickcountdownfrom>0:
                self._active_pinbutton.countdownvalue=self._active_pinbutton.dblclickcountdownfrom
            
            if self._active_pinbutton.onclicked!=None:
                self._active_pinbutton.onclicked(self._active_pinbutton)
            self._state=BUTTON_STATE_SINGLECLICK_DEBOUNCING 
            self._debounce_timer_start()
            self._lastclick_ticks=utime.ticks_ms()
        elif self._state==BUTTON_STATE_SINGLECLICK_DEBOUNCING:
            pass #debouncing - do nothing - just wait until the timer ends
        elif self._state==BUTTON_STATE_DOUBLECLICK_DEBOUNCING:
            pass #debouncing - do nothing - just wait until the timer ends
        elif self._state==BUTTON_STATE_REPEAT_DEBOUNCING:
            pass #debouncing - do nothing - just wait until the timer ends
        elif self._state==BUTTON_STATE_DOUBLECLICK_DEBOUNCED:
            self._state=BUTTON_STATE_SINGLECLICK_WAIT
        elif self._state==BUTTON_STATE_REPEAT_DEBOUNCED:
            self._state=BUTTON_STATE_SINGLECLICK_WAIT
        elif self._state==BUTTON_STATE_SINGLECLICK_DEBOUNCED:
            self._countdown_timer_start() #new state is determined in method
        elif self._state==BUTTON_STATE_DOUBLECLICK_WAIT: 
            if utime.ticks_diff(utime.ticks_ms(),self._lastclick_ticks)<self._active_pinbutton.countdownperiodms * self._active_pinbutton.dblclickcountdownfrom :
                self._countdown_timer_kill(True) #call with parameter = True to prevent calling the process method again
                self._lastclick_ticks=-1
                self._state=BUTTON_STATE_SINGLECLICK_WAIT
                if self._active_pinbutton.ondoubleclicked!=None:
                    self._active_pinbutton.ondoubleclicked(self._active_pinbutton)
                    self._state=BUTTON_STATE_DOUBLECLICK_DEBOUNCING 
                    self._debounce_timer_start()
        elif self._state==BUTTON_STATE_DOUBLECLICK_WAIT_ENDED: 
#            if self._active_pinbutton.onclicked!=None:
#                self._active_pinbutton.onclicked(self._active_pinbutton)
            if self._active_pinbutton.repeatdelay>0:
                self._state=BUTTON_STATE_REPEAT_WAIT
                self._repeat_timer_start()
            else:
                self._state=BUTTON_STATE_SINGLECLICK_WAIT
        elif self._state==BUTTON_STATE_REPEAT_WAIT: #wait hold
            if self._active_pinbutton==None or self._active_pinbutton.pin==None:
                self._state=BUTTON_STATE_SINGLECLICK_WAIT
            elif self._active_pinbutton.pin.value()==False:
                if self._active_pinbutton.onclicked!=None:
                    self._state=BUTTON_STATE_REPEAT_DEBOUNCING #state debouncing
                    self._debounce_timer_start()
            elif self._active_pinbutton.pin.value()==True:
                if self._active_pinbutton.onclicked!=None:
                    self._active_pinbutton.onclicked(self._active_pinbutton)
                self._repeat_timer_start()
        else:
            raise ValueError("Unhandled process state" + str(self._state))

        self.dbg_leave("{:<25}".format("process_state"),self._states[self._state],irqflags,self._active_pinbutton,self._active_pinbutton.pin.value())
        
    def _debounce_timer_start(self):
        self.dbg_enter("{:<25}".format("_debounce_timer_start"),self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
        if self._timer!=None:
            self._timer.init(mode=Timer.ONE_SHOT, period=self._active_pinbutton.startdelay, callback=self._debounce_timer_kill)
        self.dbg_leave("{:<25}".format("_debounce_timer_start"),self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())

    def _debounce_timer_kill(self,timerobject):
        self.dbg_enter("{:<25}".format("_debounce_timer_kill"),self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
        timerobject.deinit()
        if self._state==BUTTON_STATE_SINGLECLICK_DEBOUNCING:
            self._state=BUTTON_STATE_SINGLECLICK_DEBOUNCED
        elif self._state==BUTTON_STATE_DOUBLECLICK_DEBOUNCING:
            self._state=BUTTON_STATE_DOUBLECLICK_DEBOUNCED
        elif self._state==BUTTON_STATE_REPEAT_DEBOUNCING:
            self._state=BUTTON_STATE_REPEAT_DEBOUNCED
        self._process_state(None)
        self.dbg_leave("{:<25}".format("_debounce_timer_kill"),self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
        
    def _countdown_timer_start(self):
        self.dbg_enter("{:<25}".format("_countdown_timer_start"),self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
        if self._active_pinbutton.countdownperiodms>0 and self._active_pinbutton.dblclickcountdownfrom>0 and self._timer!=None:
            self._state=BUTTON_STATE_DOUBLECLICK_WAIT
            #self._active_pinbutton.countdownvalue=self._active_pinbutton.dblclickcountdownfrom
            self._timer.init(mode=Timer.PERIODIC, period=self._active_pinbutton.countdownperiodms, callback=self._countdown_timer_callback)
        else:
            self._state=BUTTON_STATE_REPEAT_WAIT
        self.dbg_leave("{:<25}".format("_countdown_timer_start"),self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value(),self._active_pinbutton.countdownvalue)
            
    def _countdown_timer_kill(self,alreadyprocessing):
        self.dbg_enter("{:<25}".format("_countdown_timer_kill()"),self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
        self._active_pinbutton.countdownvalue=-1
        if self._timer!=None:
            self._timer.deinit()
            if alreadyprocessing==False:
                self._state=BUTTON_STATE_DOUBLECLICK_WAIT_ENDED
                self._process_state(None)
        self.dbg_leave("{:<25}".format("_countdown_timer_kill()"),self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
    
    def _countdown_timer_callback(self,objtimer):
        self.dbg_enter("{:<25}".format("_countdown_timer_callback"),self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value(),self._active_pinbutton.countdownvalue)
        self._active_pinbutton.countdownvalue-=1
        if self._active_pinbutton.countdownvalue<0:
            self._countdown_timer_kill(False)
        elif self._active_pinbutton.ondoubleclickcountdown!=None:
            self._active_pinbutton.ondoubleclickcountdown(self._active_pinbutton)
        self.dbg_leave("{:<25}".format("_countdown_timer_callback"),self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
            
    def _repeat_timer_start(self):
        self.dbg_enter("{:<25}".format("_repeat_timer_start"),self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
        if self._timer!=None:
            self._timer.init(mode=Timer.ONE_SHOT, period=self._active_pinbutton.repeatdelay, callback=self._repeat_timer_callback)
        self.dbg_leave("{:<25}".format("_repeat_timer_start"),self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())

    def _repeat_timer_callback(self,timerobject):
        self.dbg_enter("{:<25}".format("_repeat_timer_callback"),self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
        timerobject.deinit()
        self._process_state(None)
        self.dbg_leave("{:<25}".format("_repeat_timer_callback"),self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
        
    def _reset(self):
        self.dbg_enter("{:<25}".format("_reset"),self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
        if self._timer!=None:
            self._timer.deinit()
        self._active_pinbutton.countdownvalue-=1
        self.dbg_leave("{:<25}".format("_reset"),self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
    