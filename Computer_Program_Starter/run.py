import os
from app import create_app
from config import DevelopmentConfig, ProductionConfig

env = os.environ.get("APP_ENV") or os.environ.get("FLASK_ENV") or "development"
env = env.lower()

if env in ("production", "prod"):
    config_class = ProductionConfig
else:
    config_class = DevelopmentConfig

app = create_app(config_class=config_class)

if __name__ == "__main__":
    is_production = env in ("production", "prod")
    if is_production:
        app.run(debug=False, use_reloader=False)
    else:
        app.run(debug=app.config.get("DEBUG", False))