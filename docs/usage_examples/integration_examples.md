# Integration Examples

## Flask Application Integration

```python
from flask import Flask, request, jsonify
from yapfm import YAPFileManager, FileManagerProxy
import logging

app = Flask(__name__)

# Set up configuration
config_fm = YAPFileManager("flask_config.json", auto_create=True)
config_proxy = FileManagerProxy(
    config_fm,
    enable_logging=True,
    enable_metrics=True,
    logger=logging.getLogger("flask_config")
)

@app.route('/config', methods=['GET'])
def get_config():
    """Get application configuration."""
    try:
        with config_proxy:
            return jsonify(config_proxy.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/config/<path:key>', methods=['GET'])
def get_config_key(key):
    """Get a specific configuration key."""
    try:
        with config_proxy:
            value = config_proxy.get_key(dot_key=key)
            if value is None:
                return jsonify({"error": "Key not found"}), 404
            return jsonify({"key": key, "value": value})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/config/<path:key>', methods=['POST'])
def set_config_key(key):
    """Set a specific configuration key."""
    try:
        data = request.get_json()
        if not data or 'value' not in data:
            return jsonify({"error": "Value required"}), 400
        
        with config_proxy:
            config_proxy.set_key(data['value'], dot_key=key)
            return jsonify({"key": key, "value": data['value']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
```

## Django Settings Integration

```python
# settings.py
from yapfm import YAPFileManager
import os

# Load configuration from file
config_fm = YAPFileManager("django_config.json", auto_create=True)

with config_fm:
    # Database configuration
    DATABASES = {
        'default': {
            'ENGINE': config_fm.get_key(dot_key="database.engine", default="django.db.backends.postgresql"),
            'NAME': config_fm.get_key(dot_key="database.name", default="myapp"),
            'USER': config_fm.get_key(dot_key="database.user", default="postgres"),
            'PASSWORD': config_fm.get_key(dot_key="database.password", default=""),
            'HOST': config_fm.get_key(dot_key="database.host", default="localhost"),
            'PORT': config_fm.get_key(dot_key="database.port", default="5432"),
        }
    }
    
    # Debug setting
    DEBUG = config_fm.get_key(dot_key="debug", default=False)
    
    # Secret key
    SECRET_KEY = config_fm.get_key(dot_key="secret_key", default="your-secret-key-here")
    
    # Allowed hosts
    ALLOWED_HOSTS = config_fm.get_key(dot_key="allowed_hosts", default=["localhost"])
    
    # Logging configuration
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'file': {
                'level': config_fm.get_key(dot_key="logging.level", default="INFO"),
                'class': 'logging.FileHandler',
                'filename': config_fm.get_key(dot_key="logging.file", default="django.log"),
            },
        },
        'root': {
            'handlers': ['file'],
        },
    }
```
