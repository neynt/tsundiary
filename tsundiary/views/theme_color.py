from tsundiary.views import *
from flask import Response
import colorsys

# Theme colors.
@app.route('/colors/<theme_name>/<colors>.css', methods=['GET'])
def theme_color(theme_name, colors):
    if theme_name in ['default', 'classic', 'minimal', 'misato-tachibana', 'rei-ayanami', 'saya', 'yuno']:
        return ""
    else:
        raw_h,raw_s,raw_v = map(int, colors.split(','))
        h = raw_h/360.0
        s = raw_s/100.0
        v = raw_v/100.0
        v = 0.5 + 0.5*v
        s = 0.2 * s
        r,g,b = colorsys.hsv_to_rgb(h,s,v)
        return Response("body { background-color: rgb(%d, %d, %d); }" % (r*255, g*255, b*255), mimetype='text/css')
