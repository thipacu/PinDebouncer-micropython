#author	: N.Pronk
#date	: jan 2023
#licence: published under MIT licence
#
#Description
#--------------------------------------------------------------------
#class for debugging you program, especially when working with classes
#simply print the debug output to the console
#--------------------------------------------------------------------
#seealso: simpledebugger.py
#--------------------------------------------------------------------
#
#Usage
#--------------------------------------------------------------------
#Inherit your class from debugableitem and assign a class like
#simpledebugger
#


class DebugableItem():
    """
    Description
    --------------------------------------------------------------------
    class for debugging you program, especially when working with classes
    simply print the debug output to the console
    --------------------------------------------------------------------
    seealso: simpledebugger.py
    --------------------------------------------------------------------
    
    Usage
    --------------------------------------------------------------------
    Inherit your class from debugableitem and assign a class like
    simpledebugger

    Example
    --------------------------------------------------------------------
    class Myclass(DebugableItem):
        x=1
        def mymethod(self)
            self.dbg_enter("mymethod()")
            self.dbg_out("before assign",self.x)
            x+=1
            self.dbg_out("after assign",self.x)
            self.dbg_leave("mymethod()")
    
    
    myclassinstance=Myclass()
    myclassinstance.debugger=SimpleDebugger()
    myclassinstance.debug=True
    """
    debug=False
    debugger=None
    
    def dbg_out(self, *args):
        """
        print debuginfo to the console when the debug flag is on
        """
        if self.debug==True and self.debugger!=None:
            self.debugger.dbg_out(*args)
        
    def dbg_enter(self, *args):
        """increase the 'trace' level and print debuginfo when the debug flag is on"""
        if self.debug==True and self.debugger!=None:
            self.debugger.dbg_enter(*args)
        
    def dbg_leave(self, *args):
        """decrease the 'trace' level and print debuginfo when the debug flag is on"""
        if self.debug==True and self.debugger!=None:
            self.debugger.dbg_leave(*args)
            