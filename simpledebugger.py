#--------------------------------------------------------------------
#author	: N.Pronk
#date	: jan 2023
#licence: published under MIT licence
#
#Description
#--------------------------------------------------------------------
#class for debugging you program, especially when working with classes
#simply print the debug output to the console
#--------------------------------------------------------------------

import sys
import utime

#Todo: Would like to use sys._getframe() to get and print the calling method. Micropython does not support it??

class SimpleDebugger():
    """
    Description
    --------------------------------------------------------------------
    class for debugging you program, especially when working with classes
    simply print the debug output to the console
    --------------------------------------------------------------------
    """
    currentdepth: int = 0
    debug=True
    padchars=20

    def dbg_out(self, *args):
        """
        print debuginfo when the debug flag is on prefixed with ms ticks and call level
        
        dbg_out("my info",1,2)
        
        console output with call level=0:
        xxxxxxxxxx myinfo,1,2
        """
        
        if self.debug==True:
            print('{:<25}'.format(str(utime.ticks_ms())+" : "+"|" * self.currentdepth), *args)
                
    def dbg_enter(self, *args):
        """increase the 'trace' level and print debuginfo when the debug flag is on"""
        if self.debug==True:
            print('{:<25}'.format(str(utime.ticks_ms())+" : "+"|" * self.currentdepth +"\\"), *args)
            self.currentdepth+=1
        
    def dbg_leave(self, *args):
        """decrease the 'trace' level and print debuginfo when the debug flag is on"""
        if self.debug==True:
            self.currentdepth-=1
            print('{:<25}'.format(str(utime.ticks_ms())+" : "+"|" * self.currentdepth+"/"), *args)
