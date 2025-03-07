def register(app):
    @app.cli.command('create-db')
    def create_db():
        from app import db
        db.create_all()
        print("Database created.")