import os
from tsundiary import app

PORT = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=PORT, debug=os.environ.get('DEBUG') or False)
