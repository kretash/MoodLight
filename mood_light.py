import rumps
import sys
import time
import threading

import Quartz
import LaunchServices
import Quartz.CoreGraphics as CG

from PIL import Image

import ctypes
from sdl2 import *

def screenshot(region = None):
    global state

    if region is None:
        region = CG.CGRectInfinite

    ct = time.time()

    # Create screenshot as CGImage
    image = CG.CGWindowListCreateImage(
        region,
        CG.kCGWindowListOptionOnScreenOnly,
        CG.kCGNullWindowID,
        CG.kCGWindowImageDefault)

    state.width = CG.CGImageGetWidth(image)
    state.height = CG.CGImageGetHeight(image)
    state.stride = CG.CGImageGetBytesPerRow(image)
    state.pixeldata = CG.CGDataProviderCopyData(CG.CGImageGetDataProvider(image))

    image = Image.frombuffer("RGBA", (width, height), pixeldata, "raw", "RGBA", stride, 1)
    b, g, r, a = image.split()
    image = Image.merge("RGBA", (r, g, b, a))

    print('elapsed:', time.time() - ct)

    return image

class State(object):
    def __init__(self):
        self.color_str = "none"
        self.color_menu = None
        self.enabled = False
        self.running = True
        self.screenshot_image = None
        self.status_bar = None
        self.window = None
        self.windowsurface = None

        self.image = None
        self.width = None
        self.height = None
        self.stride = None

state = State()

class StatusBarApp(rumps.App):
    @rumps.clicked("Enabled")
    def onoff(self, sender):
        global state
        sender.state = not sender.state
        state.enabled = sender.state

    @rumps.clicked("~Quit")
    def quit(self, sender):
        global state
        state.running = false
        rumps.quit_application(None)

def capture_screen():
    global state

    while state.running:
        
        if state.enabled:
            state.screenshot_image = screenshot()
        
        if state.screenshot_image is not None:
            img = state.screenshot_image.resize((960, 520), Image.ANTIALIAS)
            SDL_BlitSurface(img, None, state.windowsurface, None)
        
        SDL_UpdateWindowSurface(state.window)


def main():
    global state

    SDL_Init(SDL_INIT_VIDEO)
    state.window = SDL_CreateWindow(b"ScreenClone",
                              SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED,
                              960, 520, SDL_WINDOW_SHOWN)
    state.windowsurface = SDL_GetWindowSurface(state.window)

    surface = SDL_CreateRGBSurface(0,960,520,32,0,0,0,0)

    event = SDL_Event()
    while state.running:
        while SDL_PollEvent(ctypes.byref(event)) != 0:
            if event.type == SDL_QUIT:
                state.running = False
                break

        SDL_BlitSurface(surface, None, state.windowsurface, None)
        SDL_UpdateWindowSurface(state.window)
    #threading.Thread(target=capture_screen).start()
    
    #state.status_bar = StatusBarApp(name="mood light", icon='icon.png')
    #state.status_bar.run()

    SDL_DestroyWindow(state.window)
    SDL_Quit()

if __name__ == "__main__":
    main()