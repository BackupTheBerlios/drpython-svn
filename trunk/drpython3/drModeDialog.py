#!/usr/bin/env python


import wx
import drScrolledMessageDialog

LARGESPACER = 20

"""A custom dialog class which displays bitmap buttons asking the user
   if they want to run DrPython in Beginner or Advanced interface mode.
   There is also a checkbox which allows users to save their choice as
   a preference."""
class drModeDialog(wx.Dialog):
    
    """Creates a new drModeDialog, creates buttons, checkbox, and uses sizers to set
    the layout."""
    def __init__(self, parent):
        wx.Dialog.__init__(self, parent, -1, "Please Select a Mode", wx.Point(50,50), wx.Size(400,200), wx.DEFAULT_DIALOG_STYLE | wx.MAXIMIZE_BOX | wx.THICK_FRAME | wx.RESIZE_BORDER)
        
        # Did the user choose the advanced option?
        self.advanced = False
        
        # Button IDs
        self.ID_ADVANCED = 101
        self.ID_BEGINNER = 102
        
        # Does the user not want to be asked at start up?
        self.dontDisplayAtStart = False
        
        self.cmdSizer = wx.BoxSizer(wx.HORIZONTAL)
       
        # Bitmap buttons
        self.btnAdvanced = wx.BitmapButton(self, self.ID_ADVANCED,wx.BitmapFromImage(wx.Image(parent.bitmapdirectory + "/drAdvanced.png", wx.BITMAP_TYPE_PNG)))
        self.btnBeginner = wx.BitmapButton(self, self.ID_BEGINNER, wx.BitmapFromImage(wx.Image(parent.bitmapdirectory + "/drBeginner.png",wx.BITMAP_TYPE_PNG)))
         
        # The main sizer, spacers are used to make the layout
        # more spread out.
        self.cmdSizer.Add((LARGESPACER, LARGESPACER), 0)
        self.cmdSizer.Add(self.btnBeginner, 0, wx.SHAPED | wx.ALIGN_CENTER)
        self.cmdSizer.Add((LARGESPACER + 5, LARGESPACER + 5), 0)
        self.cmdSizer.Add(self.btnAdvanced, 0, wx.SHAPED | wx.ALIGN_CENTER)
       
        
        self.checkBox = wx.CheckBox(self,-1, "Don't show again", wx.Point(10, 150), (-1,-1),0,wx.Validator())
        
        
        self.SetAutoLayout(True)
        self.SetSizer(self.cmdSizer)
        
        self.Bind(wx.EVT_BUTTON,  self.OnbtnAdvanced, id=self.ID_ADVANCED)
        self.Bind(wx.EVT_BUTTON, self.OnBtnBeginner, id=self.ID_BEGINNER)
                  
    """When the advanced button is clicked,
    save the state of the checkbox, and set the 'advanced' variable to true."""
    def OnbtnAdvanced(self, event):
        self.dontDisplayAtStart = self.checkBox.GetValue()
        self.advanced = True
        self.Close(1)
        
    """When the beginner button is clicked,
    save the state of the checkbox, and leave the 'advanced' variable as it is,
    because it is false by default."""
    def OnBtnBeginner(self, event):
        self.dontDisplayAtStart = self.checkBox.GetValue()
        self.Close(1)
    
    """Returns if the advanced mode has been selected"""
    def getChoice(self):
        return self.advanced
    
    """Does the user want to save their selection as a preference?"""
    def getDontDisplayAtStart(self):
        return self.dontDisplayAtStart
