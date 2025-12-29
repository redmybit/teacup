import os
import sdl2
import sdl2.sdlttf as ttf
from .draw import RECT

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))

_fonts = {
    "Inter" : os.path.join(_BASE_DIR, "..", "assets", "Inter_24pt-Regular.ttf"),
    "Roboto" : os.path.join(_BASE_DIR, "..", "assets", "Roboto-Regular.ttf"),
    "Source Serif 4" : os.path.join(_BASE_DIR, "..", "assets", "IBMPlexMono-Regular.ttf"),
    "IBM Plex Mono" : os.path.join(_BASE_DIR, "..", "assets", "SourceSerif4-Regular.ttf"),
    "Noto Sans" : os.path.join(_BASE_DIR, "..", "assets", "NotoSans-Regular.ttf")
}

def init_fonts():
    """
    Init both teacup & sdl2 font systems.
    """
    ttf.TTF_Init()

def close_fonts():
    """
    Safely exit teacup font api
    """
    ttf.TTF_Quit()

def create_custom_font(path : str, name : str) -> None:
    """
    Add a custom font path to `_fonts`. Added fonts can be loaded with `load_font(name, size)`
    """

    _fonts[name] = path

def load_font(name : str, size : int):
    """
    Load a font from teacup's font api. Returns `None` if the font could not be found in the api.
    """

    if name in _fonts:
        return ttf.TTF_OpenFont(_fonts[name].encode("utf-8"), size) # convert to bytes

    return None

def get_loaded_font_names():
    return list(_fonts.keys())

class TEXT(RECT):
    def __init__(self, name="text"):
        super().__init__(name)
    
    def _render(self, pipe, renderer):
        # unload pipe
        x, y, w, h = pipe["geometry"] # borrows the same geometry from teacup.draw.RECT
        r, g, b, a = pipe["style"]["color"] # text uses color instead of background-color

        super()._render(pipe, renderer) # render the background rectangle
        rect = sdl2.SDL_Rect(x, y, w, h) # destination
        
        sdl2.SDL_SetRenderDrawColor(renderer, r, g, b, a)
        sdl2.SDL_RenderCopy(renderer, pipe["texture"], None, rect) # render the texture
        
