
import wx
from pynput import keyboard
import threading
import argparse
import os 
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1' #hide the welcome message
import pygame

KEY_X_SIZE = 40
KEY_Y_SIZE = 40

# WIDTH = 550 # row 1 should have 15 key + spacing
# HEIGHT = 300

PRESS_BG_COLOR = wx.Colour(255,210,127)
RELEASE_BG_COLOR = wx.Colour(244,244,244)
KEYBOARD_BG_COLOR = wx.Colour(165,214,167)

FONT_PATH = r"./Lexend/Lexend-VariableFont_wght.ttf"
SOUND_PATH = r"./mechanical-key-soft-short.mp3"
SOUND_ON = False

STANDARD_LAYOUT = [
            ['Esc', 'F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12'],
            ['`', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '-', '=', 'Backspace'],
            ['Tab', 'Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '[', ']', '\\'],
            ['Caps Lock', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ';', "'", 'Enter'],
            ['Shift', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', ',', '.', '/', 'Shift'],
            ['Ctrl', 'Alt', 'Space', 'Alt', 'Ctrl']
        ]

SHIFT_LAYOUT = [
            ['', '', '', '', '', '', '', '', '', '', '', '', ''],
            ['~', '!', '@', '#', '$', '%', '^', '&&', '*', '(', ')', '_', '+', ''],
            ['', '', '', '', '', '', '', '', '', '', '', '{', '}', '|'],
            ['', '', '', '', '', '', '', '', '', '', ':', "\"", ''],
            ['', '', '', '', '', '', '', '', '<', '>', '?', ''],
            ['', '', '', '', '']
        ]

def decode_ctrl_key(byte):
    # Check if the byte corresponds to a control character (0x00 to 0x1F)
    if 0x00 <= byte <= 0x1F:
        # print(f"Ctrl+{chr(byte + 64)}" )
        return chr(byte + 64)# Add 64 to convert to ASCII equivalent of Ctrl+A, Ctrl+B, etc.
    else:
        # print(hex(byte))
        pass
    return chr(byte)

pygame.mixer.init()

def play_sound():
    sound = pygame.mixer.Sound(SOUND_PATH)
    sound.play()

class Key(wx.Button):
    def __init__(self,parent,id=wx.ID_ANY,pos=(0,0),percent_w=1,percent_h=1,mainword="",subword=""):
        super().__init__(parent, id=id,pos=pos, size=(round(percent_w*KEY_X_SIZE),round(percent_h*KEY_Y_SIZE)))
        self.mainword = mainword
        self.subword = subword
        
        if (subword!=""):
            self.SetLabel(f"{subword}\n{mainword}")
        else:
            self.SetLabel(f"{mainword}")

        self.SetBackgroundColour(RELEASE_BG_COLOR)
        self.SetFont(wx.Font(10, wx.DEFAULT, wx.NORMAL, wx.BOLD, faceName=FONT_PATH))

class MyFrame(wx.Frame): # main window
    def __init__(self,parent,title):
        # super().__init__(parent,title=title, size=(WIDTH,HEIGHT))
        super().__init__(parent,title=title)

        panel = wx.Panel(self) # a panel to hold items
        framesizer = wx.GridSizer(1)
        panelsizer = wx.GridSizer(1)

        self.SetBackgroundColour(KEYBOARD_BG_COLOR)
        self.SetIcon(wx.Icon("favicon.ico", wx.BITMAP_TYPE_ICO))

        panel.SetBackgroundColour(KEYBOARD_BG_COLOR)
        panel.Enable(False) # disable the panel

        self.KeyDict = {} # to save all the buttons

        # draw the keyboard out 
        for i,row in enumerate(STANDARD_LAYOUT):
            pos_x = 0
            for j,col in enumerate(row):
                percent_w = 1
                percent_h = 1
                spacing = 0
                match col:
                    case "Esc":
                        percent_w = 1
                        spacing = KEY_X_SIZE
                    case "F4" | "F8":
                        spacing = KEY_X_SIZE//2
                    case "Tab" | "\\":
                        percent_w = 1.5 
                    case "Backspace":
                        percent_w = 2
                    case "Caps Lock" | "Enter":
                        percent_w = 2
                    case "Shift":
                        percent_w = 2.5
                    case "Ctrl" | "Alt":
                        percent_w = 2.5
                    case "Space":
                        percent_w = 5
                    case _:
                        pass
                
                button = Key(panel,percent_w=percent_w, percent_h=percent_h, pos=(pos_x,(i*(KEY_Y_SIZE))),mainword=STANDARD_LAYOUT[i][j],subword=SHIFT_LAYOUT[i][j])
                match STANDARD_LAYOUT[i][j]:
                    case "Shift" | "Ctrl" | "Alt":
                        if (STANDARD_LAYOUT[i][j].lower() not in self.KeyDict):
                            self.KeyDict[STANDARD_LAYOUT[i][j].lower()] = button
                        else:
                            self.KeyDict[f"{STANDARD_LAYOUT[i][j].lower()}_r"] = button

                    case _: # default keys
                        if (STANDARD_LAYOUT[i][j].lower() not in self.KeyDict):
                            self.KeyDict[STANDARD_LAYOUT[i][j].lower()] = button
                        if (SHIFT_LAYOUT[i][j] != "" and SHIFT_LAYOUT[i][j].lower() not in self.KeyDict):
                            self.KeyDict[SHIFT_LAYOUT[i][j].lower()] = button

                # next pos
                pos_x += round(percent_w*KEY_X_SIZE) + spacing

        # make sure the panel is always at the center
        panelsizer.Add(panel,proportion=1,flag=wx.EXPAND | wx.ALL,border=10)
        framesizer.Add(panelsizer,proportion=1,flag=wx.ALIGN_CENTER,border=0)
        self.SetSizerAndFit(framesizer)

        # read the keyboard input
        self.listener = keyboard.Listener(
            on_press=self.on_press,
            on_release=self.on_release)
        self.listener.start()
        
        # bind close event to on_close
        self.Bind(wx.EVT_CLOSE,self.on_close)

        self.Show()
    
    def on_press(self,key): # when keyboard key is pressed
        # play the mechanical keyboard sound
        if (SOUND_ON):
            threading.Thread(target=play_sound).start()

        # print('{0} on_press'.format(key))
        try:
            try:
                key.char = decode_ctrl_key(ord(key.char))
            except:
                pass

            if (key.char.lower() == "&"):
                key.char = "&&"
            if (key.char.lower() in self.KeyDict):
                self.KeyDict[key.char.lower()].SetBackgroundColour(PRESS_BG_COLOR)
        except AttributeError:
            try:
                key.char = (chr(int(str(key).replace("<","").replace(">","")))) # this conversion is for Ctrl+number
                if (key.char.lower() in self.KeyDict):
                    self.KeyDict[key.char.lower()].SetBackgroundColour(PRESS_BG_COLOR)
            except :
                pass
            match key:
                case keyboard.Key.shift_l | keyboard.Key.shift:
                    if ("shift" in self.KeyDict):
                        self.KeyDict["shift"].SetBackgroundColour(PRESS_BG_COLOR)
                    elif ("shift_l" in self.KeyDict):
                        self.KeyDict["shift_l"].SetBackgroundColour(PRESS_BG_COLOR)
                    
                case keyboard.Key.shift_r:
                    if ("shift_r" in self.KeyDict):
                        self.KeyDict["shift_r"].SetBackgroundColour(PRESS_BG_COLOR)
                    
                case keyboard.Key.alt_l | keyboard.Key.alt:
                    if ("alt" in self.KeyDict):
                        self.KeyDict["alt"].SetBackgroundColour(PRESS_BG_COLOR)
                    elif ("alt_l" in self.KeyDict):
                        self.KeyDict["alt_l"].SetBackgroundColour(PRESS_BG_COLOR)
                    
                case keyboard.Key.alt_r | keyboard.Key.alt_gr:
                    if ("alt_r" in self.KeyDict):
                        self.KeyDict["alt_r"].SetBackgroundColour(PRESS_BG_COLOR)
                    elif ("alt_gr" in self.KeyDict):
                        self.KeyDict["alt_gr"].SetBackgroundColour(PRESS_BG_COLOR)
                    
                case keyboard.Key.ctrl_l | keyboard.Key.ctrl:
                    if ("ctrl" in self.KeyDict):
                        self.KeyDict["ctrl"].SetBackgroundColour(PRESS_BG_COLOR)
                    elif ("ctrl_l" in self.KeyDict):
                        self.KeyDict["ctrl_l"].SetBackgroundColour(PRESS_BG_COLOR)
                    
                case keyboard.Key.ctrl_r:
                    if ("ctrl_r" in self.KeyDict):
                        self.KeyDict["ctrl_r"].SetBackgroundColour(PRESS_BG_COLOR)
                
                case keyboard.Key.space:
                    if ("space" in self.KeyDict):
                        self.KeyDict["space"].SetBackgroundColour(PRESS_BG_COLOR)
                    
                case keyboard.Key.tab:
                    if ("tab" in self.KeyDict):
                        self.KeyDict["tab"].SetBackgroundColour(PRESS_BG_COLOR)
                        
                case keyboard.Key.enter:
                    if ("enter" in self.KeyDict):
                        self.KeyDict["enter"].SetBackgroundColour(PRESS_BG_COLOR)
                        
                case keyboard.Key.backspace:
                    if ("backspace" in self.KeyDict):
                        self.KeyDict["backspace"].SetBackgroundColour(PRESS_BG_COLOR)
                        
                case keyboard.Key.caps_lock:
                    if ("caps lock" in self.KeyDict):
                        self.KeyDict["caps lock"].SetBackgroundColour(PRESS_BG_COLOR)
                        
                case keyboard.Key.esc:
                    if ("esc" in self.KeyDict):
                        self.KeyDict["esc"].SetBackgroundColour(PRESS_BG_COLOR)
                case _: # for f1 to f12
                    key_name = str(key).replace("Key.", "")
                    if (key_name in self.KeyDict):
                        self.KeyDict[key_name].SetBackgroundColour(PRESS_BG_COLOR)

    def on_release(self,key): # when keyboard key is release
        # print('{0} on_release'.format(key))
        try:
            try:
                key.char = decode_ctrl_key(ord(key.char))
            except:
                pass
            if (key.char.lower() == "&"):
                key.char = "&&"
            if (key.char.lower() in self.KeyDict):
                self.KeyDict[key.char.lower()].SetBackgroundColour(RELEASE_BG_COLOR)
        except AttributeError:
            try:
                key.char = (chr(int(str(key).replace("<","").replace(">","")))) # this conversion is for Ctrl+number
                if (key.char.lower() in self.KeyDict):
                    self.KeyDict[key.char.lower()].SetBackgroundColour(RELEASE_BG_COLOR)
            except :
                pass
            match key:
                case keyboard.Key.shift_l | keyboard.Key.shift:
                    if ("shift" in self.KeyDict):
                        self.KeyDict["shift"].SetBackgroundColour(RELEASE_BG_COLOR)
                    elif ("shift_l" in self.KeyDict):
                        self.KeyDict["shift_l"].SetBackgroundColour(RELEASE_BG_COLOR)
                    
                case keyboard.Key.shift_r:
                    if ("shift_r" in self.KeyDict):
                        self.KeyDict["shift_r"].SetBackgroundColour(RELEASE_BG_COLOR)
                    
                case keyboard.Key.alt_l | keyboard.Key.alt:
                    if ("alt" in self.KeyDict):
                        self.KeyDict["alt"].SetBackgroundColour(RELEASE_BG_COLOR)
                    elif ("alt_l" in self.KeyDict):
                        self.KeyDict["alt_l"].SetBackgroundColour(RELEASE_BG_COLOR)
                    
                case keyboard.Key.alt_r | keyboard.Key.alt_gr:
                    if ("alt_r" in self.KeyDict):
                        self.KeyDict["alt_r"].SetBackgroundColour(RELEASE_BG_COLOR)
                    elif ("alt_gr" in self.KeyDict):
                        self.KeyDict["alt_gr"].SetBackgroundColour(RELEASE_BG_COLOR)
                    
                case keyboard.Key.ctrl_l | keyboard.Key.ctrl:
                    if ("ctrl" in self.KeyDict):
                        self.KeyDict["ctrl"].SetBackgroundColour(RELEASE_BG_COLOR)
                    elif ("ctrl_l" in self.KeyDict):
                        self.KeyDict["ctrl_l"].SetBackgroundColour(RELEASE_BG_COLOR)
                    
                case keyboard.Key.ctrl_r:
                    if ("ctrl_r" in self.KeyDict):
                        self.KeyDict["ctrl_r"].SetBackgroundColour(RELEASE_BG_COLOR)
                
                case keyboard.Key.space:
                    if ("space" in self.KeyDict):
                        self.KeyDict["space"].SetBackgroundColour(RELEASE_BG_COLOR)
                    
                case keyboard.Key.tab:
                    if ("tab" in self.KeyDict):
                        self.KeyDict["tab"].SetBackgroundColour(RELEASE_BG_COLOR)
                        
                case keyboard.Key.enter:
                    if ("enter" in self.KeyDict):
                        self.KeyDict["enter"].SetBackgroundColour(RELEASE_BG_COLOR)
                        
                case keyboard.Key.backspace:
                    if ("backspace" in self.KeyDict):
                        self.KeyDict["backspace"].SetBackgroundColour(RELEASE_BG_COLOR)
                        
                case keyboard.Key.caps_lock:
                    if ("caps lock" in self.KeyDict):
                        self.KeyDict["caps lock"].SetBackgroundColour(RELEASE_BG_COLOR)
                        
                case keyboard.Key.esc:
                    if ("esc" in self.KeyDict):
                        self.KeyDict["esc"].SetBackgroundColour(RELEASE_BG_COLOR)
                case _: # for f1 to f12
                    key_name = str(key).replace("Key.", "")
                    if (key_name in self.KeyDict):
                        self.KeyDict[key_name].SetBackgroundColour(RELEASE_BG_COLOR)

    def on_close(self,event):
        self.listener.stop()
        self.Destroy()
        pass

class MyApp(wx.App):
    def OnInit(self):
        frame = MyFrame(None,"Keyboard Visualizer")
        frame.SetWindowStyleFlag(wx.DEFAULT_FRAME_STYLE & ~(wx.MINIMIZE_BOX))
        return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Keyboard visualizer arguments")
    
    parser.add_argument('--soundon', action='store_true', help="Enable sound.")
    
    # Parse the arguments
    args = parser.parse_args()
    
    if args.soundon:
        SOUND_ON = True
    else:
        SOUND_ON = False
    app = MyApp()
    app.MainLoop()