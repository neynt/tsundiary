import os
from tsundiary import app, ensure_db_exists

PORT = int(os.environ.get('PORT', 5000))
ensure_db_exists()
app.run(host='0.0.0.0', port=PORT, debug=os.environ.get('DEBUG') or False)
