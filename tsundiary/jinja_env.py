# encoding=utf-8
from tsundiary import app

app.jinja_env.globals.update(theme_nicename = {
    'classic': 'Classic Orange',
    'tsun-chan': 'Classic Orange w/ Tsundiary-chan',
    'minimal': 'Minimal Black/Grey',
    'misato-tachibana': 'Misato Tachibana',
    'rei-ayanami': 'Rei Ayanami',
    'saya': 'Saya',
    'yuno': 'Yuno Gasai',
    'hitagi': 'Hitagi Senjougahara',
    'kyoko-sakura': 'Kyoko Sakura',
    'colorful': 'Based on favorite color'
})
app.jinja_env.globals.update(themes = ['classic', 'tsun-chan', 'minimal', 'misato-tachibana', 'rei-ayanami', 'saya', 'yuno', 'colorful'])

app.jinja_env.globals.update(theme_creds = {
    'misato-tachibana': 'Misato Tachibana source: Nichijou OP1.',
    'rei-ayanami': '<a href="http://megadud20.deviantart.com/art/Rei-Ayanami-Vector-214547575">Rei source</a>.',
    'saya': u'<a href="http://e-shuushuu.net/image/34277/">Saya source</a>. Artist: 中央東口 (Chuuou Higashiguchi).',
    'yuno': '<a href="http://xyanderegirl.deviantart.com/art/Yuno-Gasai-Render-293856645">Yuno source</a>.',
    'kyoko-sakura': '<a href="http://3071527.deviantart.com/art/kyoko-sakura-376238110">Kyoko source</a>.'
})

app.jinja_env.globals.update(theme_colors = [
    ('Red', '0,100,100'),
    ('Orange', '35,100,100'),
    ('Yellow', '50,100,100'),
    ('Green', '120,100,80'),
    ('Cyan', '180,100,80'),
    ('Blue', '215,100,100'),
    ('Purple', '270,100,100'),
    ('Black', '0,0,0'),
    ('Grey', '0,0,70'),
    ('White', '0,0,100'),
])
