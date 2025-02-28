from datetime import datetime
from app import db
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.dialects.postgresql import JSON


class Dashboard(db.Model):
    """Model dashboardu - zbiór widgetów i wizualizacji"""
    __tablename__ = 'dashboards'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    layout = db.Column(db.String(20), default='grid')
    is_public = db.Column(db.Boolean, default=False)
    is_template = db.Column(db.Boolean, default=False)
    theme = db.Column(db.String(20), default='light')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacje
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    widgets = db.relationship('Widget', backref='dashboard', lazy='dynamic', cascade='all, delete-orphan')
    
    # Uprawnienia dostępu innych użytkowników
    collaborators = db.relationship('DashboardCollaborator', backref='dashboard', cascade='all, delete-orphan')
    
    @hybrid_property
    def widget_count(self):
        """Zwraca liczbę widgetów w dashboardzie"""
        return self.widgets.count()
    
    def __repr__(self):
        return f'<Dashboard {self.title}>'


class Widget(db.Model):
    """Model widgetu - pojedynczej wizualizacji na dashboardzie"""
    __tablename__ = 'widgets'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    widget_type = db.Column(db.String(50), nullable=False)  # chart, table, metric, etc.
    chart_type = db.Column(db.String(50))  # bar, line, pie, etc. (dla widgetów typu chart)
    position_x = db.Column(db.Integer, default=0)
    position_y = db.Column(db.Integer, default=0)
    width = db.Column(db.Integer, default=4)
    height = db.Column(db.Integer, default=4)
    settings = db.Column(JSON, default={})
    query = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacje
    dashboard_id = db.Column(db.Integer, db.ForeignKey('dashboards.id'))
    data_source_id = db.Column(db.Integer, db.ForeignKey('data_sources.id'))
    
    def __repr__(self):
        return f'<Widget {self.title} ({self.widget_type})>'


class DataSource(db.Model):
    """Model źródła danych - połączenia do bazy danych lub pliku"""
    __tablename__ = 'data_sources'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text)
    source_type = db.Column(db.String(50), nullable=False)  # database, file, api, etc.
    connection_details = db.Column(JSON, default={})
    is_active = db.Column(db.Boolean, default=True)
    refresh_rate = db.Column(db.Integer, default=0)  # w minutach, 0 = brak automatycznego odświeżania
    last_refresh = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacje
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    widgets = db.relationship('Widget', backref='data_source', lazy='dynamic')
    
    def __repr__(self):
        return f'<DataSource {self.name} ({self.source_type})>'


class DashboardCollaborator(db.Model):
    """Model współpracownika dashboardu - użytkownik z dostępem do dashboardu"""
    __tablename__ = 'dashboard_collaborators'
    
    id = db.Column(db.Integer, primary_key=True)
    dashboard_id = db.Column(db.Integer, db.ForeignKey('dashboards.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    permission_level = db.Column(db.String(20), default='view')  # view, edit, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacja z użytkownikiem
    user = db.relationship('User', backref='shared_dashboards')
    
    def __repr__(self):
        return f'<DashboardCollaborator dashboard_id={self.dashboard_id} user_id={self.user_id}>'