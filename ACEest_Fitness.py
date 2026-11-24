"""
ACEest_Fitness.py - Production Flask application entry point.
Maintained for backwards-compatibility with course assignment specification.
"""
from aceest import create_app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
