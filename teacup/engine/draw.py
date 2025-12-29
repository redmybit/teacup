import sdl2

class Shape:
    def __init__(self, name):
        self.name = name

    def _render(self, pipe, renderer): pass

class RECT(Shape):
    def __init__(self, name="rectangle"):
        super().__init__(name)

    def _render(self, pipe, renderer):
        # geometry
        x, y, w, h = pipe["geometry"]
        rect = sdl2.SDL_Rect(x, y, w, h) # xywh

        # color
        r, g, b, a = pipe["style"]["background-color"]
        sdl2.SDL_SetRenderDrawColor(renderer, r, g, b, a) # rgba

        # render
        sdl2.SDL_RenderFillRect(renderer, rect)
        return super()._render(pipe, renderer)

class ELLIPSE(Shape):
    def __init__(self, name="ellipse"):
        super().__init__(name)
    
    def _render(self, pipe, renderer):
        # color
        r, g, b, a = pipe["style"]["background-color"]
        sdl2.SDL_SetRenderDrawColor(renderer, r, g, b, a) # rgba

        # avoid lookup
        cx, cy, width, height = pipe["geometry"]

        # temporary solution (thanks chatgpt)
        if width <= 0 or height <= 0:
            return super()._render(pipe, renderer)

        rx = width // 2
        ry = height // 2
        if rx <= 0 or ry <= 0:
            sdl2.SDL_RenderDrawLine(renderer, cx - rx, cy, cx + rx, cy)
            return super()._render(pipe, renderer)

        rx2 = rx * rx
        ry2 = ry * ry
        two_rx2 = rx2 << 1
        two_ry2 = ry2 << 1

        x = 0
        y = ry

        # Region 1 (scaled by 4)
        p1 = (ry2 << 2) - (rx2 * ry << 2) + rx2
        dx = 0
        dy = two_rx2 * y

        while dx < dy:
            # spans at cy +- y, half-width x
            sdl2.SDL_RenderDrawLine(renderer, cx - x, cy + y, cx + x, cy + y)
            if y:
                sdl2.SDL_RenderDrawLine(renderer, cx - x, cy - y, cx + x, cy - y)

            x += 1
            dx += two_ry2

            if p1 < 0:
                p1 += (dx << 2) + (ry2 << 2)
            else:
                y -= 1
                dy -= two_rx2
                p1 += ((dx - dy) << 2) + (ry2 << 2)

        # Region 2 (scaled by 4)
        x2p1 = (x << 1) + 1
        ym1 = y - 1
        p2 = (ry2 * x2p1 * x2p1) + (rx2 * ((ym1 << 1) * (ym1 << 1))) - (rx2 * ry2 << 2)

        while y >= 0:
            sdl2.SDL_RenderDrawLine(renderer, cx - x, cy + y, cx + x, cy + y)
            if y:
                sdl2.SDL_RenderDrawLine(renderer, cx - x, cy - y, cx + x, cy - y)

            y -= 1
            dy -= two_rx2

            if p2 > 0:
                p2 += (rx2 << 2) - (dy << 2)
            else:
                x += 1
                dx += two_ry2
                p2 += ((dx - dy) << 2) + (rx2 << 2)

        return super()._render(pipe, renderer)
