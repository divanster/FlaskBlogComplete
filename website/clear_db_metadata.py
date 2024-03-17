from __init__ import create_app, db



# Initialize the app and bind the SQLAlchemy object to it
app = create_app()
db.init_app(app)

# Clear the metadata
# db.metadata.clear()
db.drop_all()
