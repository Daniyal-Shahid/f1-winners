from flask import Flask
from flask_cors import CORS
import logging
from routes.api import api_bp

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": ["http://localhost:5173"]}})
logging.basicConfig(level=logging.INFO)

# Register blueprints
app.register_blueprint(api_bp, url_prefix='/api')

if __name__ == '__main__':
    app.run(debug=True)
    