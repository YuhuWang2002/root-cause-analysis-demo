import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from models import db

def create_app():
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}})
    
    db_path = os.path.join(os.path.dirname(__file__), 'rca.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
        print(f"Database created at: {db_path}")
    
    from routes import projects, canvas, nodes, ontology, data_analysis, dashboards, root_cause
    app.register_blueprint(projects.bp)
    app.register_blueprint(canvas.bp)
    app.register_blueprint(nodes.bp)
    app.register_blueprint(ontology.bp)
    app.register_blueprint(data_analysis.bp)
    app.register_blueprint(dashboards.bp)
    app.register_blueprint(root_cause.bp)
    
    @app.route('/api/projects', methods=['OPTIONS'])
    def handle_options():
        return '', 204
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=False, port=5000, use_reloader=False)
