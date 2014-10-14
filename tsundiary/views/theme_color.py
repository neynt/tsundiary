from tsundiary.views import *
from flask import Response
import colorsys

class Color():
    def __init__(self, h, s, v):
        self.h = h/360.0
        self.s = s/100.0
        self.v = v/100.0

    def getRGB(self):
        print("cuz we're a", self.h, self.s, self.v)
        return colorsys.hsv_to_rgb(self.h,self.s,self.v)

    def getHexRGB(self):
        r,g,b = self.getRGB()
        print(r, g, b, "is how we do")
        r = min(r*256, 255)
        g = min(g*256, 255)
        b = min(b*256, 255)
        return "#%02x%02x%02x" % (r,g,b)

    def getBrightness(self):
        """ Calculates the perceived brightness of a color (0.0, 1.0) """
        r,g,b = self.getRGB()
        return (0.241*r*r + 0.691*g*g + 0.068*b*b)**0.5

    def scaleBrightness(self, max_val):
        self.v *= max_val

    def mapValue(self, min_val, max_val):
        self.v = min_val + self.v * (max_val-min_val)

    def scaleSaturation(self, max_sat):
        """ Linearly maps the existing saturation (0.0, 1.0) to a new range (0, max_sat). """
        self.s = self.s * max_sat

# Theme colors.
@app.route('/colors/<theme_name>/<colors>.css', methods=['GET'])
def theme_color(theme_name, colors):
    h,s,v = map(int, colors.split(','))
    base = Color(h, s, v)
    colors = []
    if theme_name in ['default', 'classic', 'minimal', 'misato-tachibana', 'rei-ayanami', 'saya', 'yuno']:
        return Response("", mimetype='text/css')
    elif theme_name == 'colorful':
        bg = Color(h, s, v)
        bg.mapValue(0.5, 1.0)
        bg.scaleSaturation(0.1)
        btn = Color(h, s, v)
        if btn.getBrightness() > 0.6:
             btn.scaleBrightness(0.8)
        colors.append("body { background-color: %s; }" % bg.getHexRGB())
        colors.append("a { color: %s; }" % btn.getHexRGB())
        colors.append("div#nav a { color: %s; }" % btn.getHexRGB())
        colors.append("div#nav a.cur_page { border-bottom-color: %s; }" % btn.getHexRGB())
        return Response('\n'.join(colors), mimetype='text/css')
