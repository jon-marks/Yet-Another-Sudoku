import wx

from globals import *

# Timer States
STOPPED = 0
RUNNING = 1
PAUSED = 2

Spinner = "|/-\\"

class GameTimer(wx.Timer):

    def __init__(self, parent):
        self.Parent = parent
        wx.Timer.__init__(self)
        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.Bind(wx.EVT_TIMER, self.on_tick)
        self.Start(1000)
        self.Seconds = self.Ticks = 0
        self.State = STOPPED
        self.SpinStatus = ""

    def on_close(self, e):
        self.Stop()
        e.Skip()
        wx.CallAfter(self.Destroy)

    def on_tick(self, e):
        if self.State == RUNNING:
            self.Seconds += 1
            s = self.Seconds%60
            m = (self.Seconds//60)%60
            h = (self.Seconds//3600)%99
            sTime = f"{h:02d}:{m:02d}:{s:02d}"
            self.Parent.update_statusbar_time(sTime)

    def start(self):
        self.Seconds = 0
        self.State = RUNNING
        self.Parent.update_statusbar_time("00:00:00")

    def stop(self):
        self.Seconds = 0
        self.State = STOPPED
        self.Parent.update_statusbar_time("00:00:00")

    def pause(self):
        self.State = PAUSED

    def resume(self):
        self.State = RUNNING
