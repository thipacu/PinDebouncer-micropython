# PinDebouncer-micropython

Pinwrapper and pin-debouncer for micropython (Tested on Raspberry Pico)

-My first ever (micro)python project

Possibilities
-Interrupt based handling for when a button is clicked - double clicked - or held.
-seperate callbacks for onclicked, ondoubleclicked, omdoubleclickedcountdown
-adjustable countdown, countdowndelat per button
-Monitoring of multiple buttons by one class
-Countdown on button (for example 10 countdown's whereafter a callback function is executed)

Files:
pinmonitortest.py - the actual program you have to run to see it work
pinbutton.py - wrapper for pin to use a pin as a interrupt based button
pinmonitor.py - class for monitoring the defined buttons - see pinmonitortest.py for example
debugableitem.py - class you have to inherit from to use the simple debugger
simpledebugger.py - simple debugger that produces console output 

published under MIT licence, N.Pronk, Jan 2023
