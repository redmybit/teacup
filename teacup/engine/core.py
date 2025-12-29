import sdl2
import sdl2.ext
import sdl2.sdlttf as ttf
import time

# module local imports
from . import draw
from . import font
from . import style

_windows = [] # list of all window objects created
_event = None

def init() -> None: 
    """
    Initializes Teacup and SDL2
    """
    sdl2.ext.init()
    font.init_fonts()

    global _event # init after sdl2 inits
    _event = sdl2.SDL_Event()

def done() -> None:
    """
    Quits Teacup and SDL2
    """ 
    font.close_fonts()
    sdl2.ext.quit()

def _window_by_wid(wid):
    """
    Retrieve a window by it's unique wid.
    """

    for w in _windows:
        if w.wid == wid:
            return w
    return None

def register_window(window) -> None:
    """
    Adds a window to the `_windows` poll list for Teacup. Will not allow you to add a window more than
    once.
    """

    if _window_by_wid(window.wid) is None:
        _windows.append(window)

def RUNNING() -> bool:
    """
    Returns `True` if there is atleast 1 window alive. Returns `False` if otherwise.
    """

    return len(_windows) > 0

def sleep(n) -> None:
    """
    Tell sdl2 to wait for n ms
    """

    sdl2.SDL_Delay(n)

def display(fps : int = 0) -> float:
    """
    Shortcuts sdl2's event system. Additionally renders any registered windows. Returns `deltatime`
    in seconds. Caps ALL windows to the given `fps` parameter (uncaps if `fps <= 0`).
    """

    before = time.perf_counter()

    while sdl2.SDL_PollEvent(_event):
        if _event.type == sdl2.SDL_WINDOWEVENT:
            if _event.window.event == sdl2.SDL_WINDOWEVENT_CLOSE:
                wid = _event.window.windowID # get the window id
                _window_by_wid(wid).destroy() # close the window

        elif _event.type == sdl2.SDL_QUIT: # called in sdl2.ext.quit() treat as shutdown
            for window in _windows:
                window._open = False

    for window in _windows: # draw the windows
        if window._open:
            window._draw()
    
    
    dif = time.perf_counter() - before

    if fps <= 0: return dif # uncapped

    dtc = 1 / fps - dif # diff between expected dt and actual dt
    if dtc > 0: 
        sleep(int(dtc * 1000)) # wait for the dt to catch up (convert to ms)
        return 1 / fps
    
    return 1 / fps - dtc # dtc < 0 so return a higher dt b/c the renderer is "behind"

class ScreenObject:
    def __init__(self, name : str, styl : dict) -> None:
        """
        Teacup internal class used for the parent of anything that eventually draws on screen. Can
        be used to create custom screen objects.

        - `name` (str): internal name of the object used for debugging
        - `styl` (dict): CSS styling in dict format.
        """

        self.name = name
        self._style = style.get_style_template()
        if styl:
            for k in styl:
                self._style[k] = styl[k]

        self.parent = None # default as None

    @property
    def style(self):
        """
        The style of this object.
        """
        return self._style

    @style.setter
    def style(self, value : dict):
        self._style = style.get_style_template()
        for k in value:
            self._style[k] = value[k]

        self._bake()
        
    def _render(self, pipeline : list) -> bool:
        if self.parent is None: return False # did not render

        for pipe in pipeline: # render each pipe seperately
            self.parent._render_pipe(pipe)
        
        return True # sucessfully rendered

    def _backwards_attach(self, parent) -> None:
        """
        Called when `my_win.attach(...)`, adds the window as a parent to the screen object.
        """
        self.parent = parent

    def _bake(self): pass

class Rectangle(ScreenObject):
    def __init__(self, x, y, width, height, style = None):
        """
        Draw rectangles on screen. x, y is the upper left corner of the rectangle.
        """

        super().__init__("rectangle", style) # name matches with draw.RECT

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self._bake()
    
    def _bake(self):
        self.geometry = (
            int(self.x),
            int(self.y),
            int(self.width),
            int(self.height)
        )
    
    def _render(self):
        self._bake()
        pipeline = [{ # custom pipeline
            "style": self._style,
            "shape": draw.RECT(), # pull from teacup.draw.RECT
            "geometry": self.geometry # xywh
        }]
        return super()._render(pipeline) # use ScreenObject's method for rendering
    
class Ellipse(ScreenObject):
    def __init__(self, x, y, width, height, style = None):
        """
        Draw circles & ovals. x, y is the upper left corner of the ellipse.
        """

        super().__init__("ellipse", style)

        self.x = x
        self.y = y
        self.width = width
        self.height = height

        self._bake()

    def _bake(self):
        self.geometry = (
            int(self.x + self.width / 2),
            int(self.y + self.height / 2),
            int(self.width),
            int(self.height)
        )
    
    def _render(self):
        self._bake()
        pipeline = [{
            "style": self._style,
            "shape": draw.ELLIPSE(),
            "geometry": self.geometry # cx cy w h
        }]

        return super()._render(pipeline)

class Text(ScreenObject):
    def __init__(self, x : int, y : int, text : str, style = None) -> None:
        """
        Draw text onscreen. font, size and color are stored in `style` as `font-family`,
        `font-size` and `color`.
        """

        super().__init__("text", style)

        self.text = text

        self.x = x
        self.y = y
        self._width = 0
        self._height = 0

        self._old_style = style.copy()

    def _backwards_attach(self, parent):
        super()._backwards_attach(parent)
        self._bake_style(override=True) # avoid baking when self.parent is None
    
    def _bake(self): # bakes both geometry & style
        self._bake_style()
        self.geometry = (
            self.x,
            self.y,
            self._width,
            self._height
        )

        self._old_style = self._style.copy()
        
    def _bake_style(self, override=False):
        """
        If the style is changed recreate the text surface and save it to a new texture.
        """

        # check if color, font-family or font-size changed
        if override or self._old_style["color"] != self._style["color"] or self._old_style["font-family"] != self._style["font-family"] or self._old_style["font-size"] != self._style["font-size"]:
            color = sdl2.SDL_Color(*self._style["color"]) # unpack color
            font_family = self._style["font-family"]
            size = self._style["font-size"]

            font_ = font.load_font(font_family, size)

            # encode text to bytes
            surface = ttf.TTF_RenderUTF8_Blended(font_, self.text.encode("utf-8"), color)
            self.texture = sdl2.SDL_CreateTextureFromSurface(self.parent.renderer, surface)

            self._width = surface.contents.w
            self._height = surface.contents.h

            sdl2.SDL_FreeSurface(surface)

    def _render(self):
        self._bake()
        pipeline = [{
            "style": self.style,
            "shape": font.TEXT(),
            "geometry": self.geometry,
            "texture": self.texture
        }]

        return super()._render(pipeline)

class Window(sdl2.ext.Window):
    def __init__(self, title : str, size : tuple, styl=None, position=None, flags=None) -> None:
        """
        Wraps `sdl2.ext.Window`

        - `title` (str): title of the window
        - `size` (tuple): size of the window (width, height)
        - `styl` (dict | None): window styling
        - `position` (tuple | None): where the window will open at (upper left corner)
        - `flag` (int | None): custom flags the window will have on opening
        """

        self.age = 0
        self.children = []
        self._style = style.get_style_template()

        if styl:
            for k in styl:
                self._style[k] = styl[k]

        super().__init__(title, size, position, flags) # init sdl2 prior to teacup init

        self.wid = sdl2.SDL_GetWindowID(self.window)
        register_window(self)

        self._open = True
        self.show() # show the window
        self.renderer = sdl2.SDL_CreateRenderer(self.window, -1, sdl2.SDL_RENDERER_ACCELERATED)
        sdl2.SDL_SetRenderDrawBlendMode(self.renderer, sdl2.SDL_BLENDMODE_BLEND) # open up alpha channel
    
    def destroy(self) -> None:
        """
        Safely destroy the window.
        """

        self._open = False
        sdl2.SDL_DestroyRenderer(self.renderer) # sdl2 cleanup
        sdl2.SDL_DestroyWindow(self.window)
        _windows.remove(self) # remove from global list

    def attach(self, obj : ScreenObject) -> int:
        """
        Attach a `ScreenObject` to this window. It will be rendered alongside the window.
        Returns the index of the `ScreenObject` in the attached window's children list.
        """

        obj._backwards_attach(self) # link the window to the ScreenObject
        self.children.append(obj)
        return len(self.children) - 1 # already added so -1
    
    def _render_pipe(self, pipe):
        pipe["shape"]._render(pipe, self.renderer) # internally call draw.RECT()._render

    def _render_self(self):
        r, g, b, a = self._style["background-color"]
        sdl2.SDL_SetRenderDrawColor(self.renderer, r, g, b, a) # "erase" window
        sdl2.SDL_RenderClear(self.renderer)

    def _render_children(self):
        for child in self.children:
            child._render()

    def _draw(self):
        self.age += 1
        self._render_self()
        self._render_children()
        sdl2.SDL_RenderPresent(self.renderer) # push renders to sdl2 render buffer

    # borrows from ScreenObject
    @property
    def style(self):
        """
        The style of the window.
        """
        return self._style

    @style.setter
    def style(self, value : dict):
        self._style = style.get_style_template()
        for k in value:
            self._style[k] = value[k]
