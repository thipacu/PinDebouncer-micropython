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
BUTTON_STATE_WAIT_CLICK=0
BUTTON_STATE_DEBOUNCING=1
BUTTON_STATE_DEBOUNCED=2
BUTTON_STATE_WAIT_DOUBLECLICK=3
BUTTON_STATE_WAIT_DOUBLECLICK_ENDED=4
BUTTON_STATE_WAIT_HOLD=5
BUTTON_STATE_DEBOUNCING_DBL=6
BUTTON_STATE_DEBOUNCED_DBL=7

class PinMonitor(DebugableItem):
   
    #private    
    _timer=Timer(-1)
    _pinbuttons=[]
    _instance = None
    _activepin= None
    _previouspin = None
    _lastclick_ticks = -1
    _timercallcount=0
    _2ndclick_maxtimercount=1
    _state=BUTTON_STATE_WAIT_CLICK
    
    #states as text array because of lack of enums for informational purposes
    _states=[ \
        "BUTTON_STATE_WAIT_CLICK" \
        , "BUTTON_STATE_DEBOUNCING" \
        , "BUTTON_STATE_DEBOUNCED" \
        , "BUTTON_STATE_WAIT_DOUBLECLICK=3" \
        , "BUTTON_STATE_WAIT_DOUBLECLICK_ENDED" \
        , "BUTTON_STATE_WAIT_HOLD" \
        , "BUTTON_STATE_DEBOUNCING_DBL" \
        , "BUTTON_STATE_DEBOUNCED_DBL" \
        ]
    
    delay=200
    repeatdelay=100
    
#	 implement new to use as singleton   
#    def __new__(self):
#        if self._instance is None:
#            self._instance = super(PinMonitor, self).__new__(self)
#            # Put any initialization here.
#        return self._instance
    
    def registerpinbutton(self, pinbutton: PinButton):
        self.dbg_enter("registerpin")
        self._pinbuttons.append(pinbutton)
        pinbutton.pin.irq(handler=self._process_state, trigger=Pin.IRQ_RISING)
        self._active_pinbutton=pinbutton
        self._previous_pinbutton=pinbutton
        self.dbg_leave("registerpin")
            
    def unregisterpin(self, pinbutton: PinButton):
        self._reset()
        self._pinbuttons.remove(pinbutton)
        founditem.pin.irq(handler=None, trigger=Pin.IRQ_RISING)
        if self._active_pinbutton==pinbutton:
            self._active_pinbutton=None
        if self._previous_pinbutton==pinbutton:
            self._previous_pinbutton=None

    def _process_state(self,irqflags):
        self.dbg_enter("process_state",self._states[self._state],irqflags,self._active_pinbutton,self._active_pinbutton.pin.value())
        if irqflags!=None:
            self._previous_pinbutton=self._active_pinbutton
            self._active_pinbutton=next((x for x in self._pinbuttons if x.pin==irqflags ))
            if self._previous_pinbutton!=self._active_pinbutton:
                self._timer.deinit()
                self._state=BUTTON_STATE_WAIT_CLICK
        
        if self._state==BUTTON_STATE_WAIT_CLICK:
            self._state=BUTTON_STATE_DEBOUNCING 
            self._debounce_timer_start()
            self._lastclick_ticks=utime.ticks_ms()
        elif self._state==BUTTON_STATE_DEBOUNCING or self._state==BUTTON_STATE_DEBOUNCING_DBL:
            pass #debouncing - do nothing - just wait until the timer ends
        elif self._state==BUTTON_STATE_DEBOUNCED_DBL:
            self._state=BUTTON_STATE_WAIT_CLICK
        elif self._state==BUTTON_STATE_DEBOUNCED:
            self._2ndclick_timer_start() #new state is determined in method
        elif self._state==BUTTON_STATE_WAIT_DOUBLECLICK: 
            self.dbg_out("BUTTON_STATE_WAIT_DOUBLECLICK 1",self._state,irqflags,self._active_pinbutton,self._active_pinbutton.pin.value())
            if utime.ticks_diff(utime.ticks_ms(),self._lastclick_ticks)<self._active_pinbutton.dblclickperiodms * self._active_pinbutton.dblclickcountdownfrom :
                self.dbg_out("BUTTON_STATE_WAIT_DOUBLECLICK 2",self._state,irqflags,self._active_pinbutton,self._active_pinbutton.pin.value())
                self._2ndclick_timer_kill(True) #call with parameter = True to prevent calling the process method again
                self._lastclick_ticks=-1
                self._state=BUTTON_STATE_WAIT_CLICK
                if self._active_pinbutton.ondoubleclicked!=None:
                    self._active_pinbutton.ondoubleclicked(irqflags)
                    self._state=BUTTON_STATE_DEBOUNCING_DBL #state debouncing
                    self._debounce_timer_start()
        elif self._state==BUTTON_STATE_WAIT_DOUBLECLICK_ENDED: #wait doubleclick ended
            if self._active_pinbutton.onclicked!=None:
                self._active_pinbutton.onclicked(irqflags)
            if self.repeatdelay>0:
                self._state=BUTTON_STATE_WAIT_HOLD
                self._hold_timer_start()
            else
                self._state=BUTTON_STATE_WAIT_CLICK
                
        elif self._state==BUTTON_STATE_WAIT_HOLD: #wait hold
            if self._active_pinbutton==None or self._active_pinbutton.pin==None or self._active_pinbutton.pin.value()==False:
                self._state=BUTTON_STATE_WAIT_CLICK
            elif self._active_pinbutton.pin.value()==True:
                if self._active_pinbutton.onclicked!=None:
                    self._active_pinbutton.onclicked(irqflags)
                self._hold_timer_start()
        else:
            raise ValueError("Unhandled process state" + str(self._state))

        self.dbg_leave("process_state",self._states[self._state],irqflags,self._active_pinbutton,self._active_pinbutton.pin.value())
        
    def _debounce_timer_start(self):
        self.dbg_enter("_debounce_timer_start",self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
        if self._timer!=None:
            self._timer.init(mode=Timer.ONE_SHOT, period=self.delay, callback=self._debounce_timer_kill)
        self.dbg_leave("_debounce_timer_start",self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())

    def _debounce_timer_kill(self,timerobject):
        self.dbg_enter("_debounce_timer_kill",self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
        timerobject.deinit()
        if self._state==BUTTON_STATE_DEBOUNCING:
            self._state=BUTTON_STATE_DEBOUNCED
        elif self._state==BUTTON_STATE_DEBOUNCING_DBL:
            self._state=BUTTON_STATE_DEBOUNCED_DBL
        self._process_state(None)
        self.dbg_leave("_debounce_timer_kill",self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
        
    def _2ndclick_timer_start(self):
        self.dbg_enter("_2ndclick_timer_start",self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
        if self._active_pinbutton.dblclickperiodms>0 and self._active_pinbutton.dblclickcountdownfrom>0 and self._timer!=None:
            self._state=BUTTON_STATE_WAIT_DOUBLECLICK
            self._timercallcount=self._active_pinbutton.dblclickcountdownfrom
            self._timer.init(mode=Timer.PERIODIC, period=self._active_pinbutton.dblclickperiodms, callback=self._2ndclick_timer_callback)
        else:
            self._state=BUTTON_STATE_WAIT_HOLD
        self.dbg_leave("_2ndclick_timer_start",self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value(),self._timercallcount)
            
    def _2ndclick_timer_kill(self,alreadyprocessing):
        self.dbg_enter("_2ndclick_timer_kill()",self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
        self._timercallcount=-1
        if self._timer!=None:
            self._timer.deinit()
            if alreadyprocessing==False:
                self._state=BUTTON_STATE_WAIT_DOUBLECLICK_ENDED
                self._process_state(None)
        self.dbg_leave("_2ndclick_timer_kill()",self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
    
    def _2ndclick_timer_callback(self,objtimer):
        self.dbg_enter("_2ndclick_timer_callback",self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value(),self._timercallcount)
        self._timercallcount-=1
        if self._timercallcount<=0:
            self._2ndclick_timer_kill(False)
        elif self._active_pinbutton.ondoubleclickdecount!=None:
            self._active_pinbutton.ondoubleclickdecount(self._timercallcount)
        self.dbg_leave("_2ndclick_timer_callback",self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value(),self._timercallcount)
            
    def _hold_timer_start(self):
        self.dbg_enter("_hold_timer_start",self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
        if self._timer!=None:
            self._timer.init(mode=Timer.ONE_SHOT, period=self.repeatdelay, callback=self._hold_timer_callback)
        self.dbg_leave("_hold_timer_start",self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())

    def _hold_timer_callback(self,timerobject):
        self.dbg_enter("_hold_timer_callback",self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
        timerobject.deinit()
        self._process_state(None)
        self.dbg_leave("_hold_timer_callback",self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
        
    def _reset(self):
        self.dbg_enter("_reset",self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
        if self._timer!=None:
            self._timer.deinit()
        self._timercallcount-=1
        self.dbg_leave("_reset",self._states[self._state],self._active_pinbutton,self._active_pinbutton.pin.value())
    