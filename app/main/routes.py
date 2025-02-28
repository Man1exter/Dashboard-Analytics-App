from flask import render_template, redirect, url_for, request, current_app
from flask_login import current_user, login_required
from app.main import bp
from app.dashboard.models import Dashboard
from sqlalchemy import desc


@bp.route('/')
def index():
    """Strona główna aplikacji"""
    if current_user.is_authenticated:
        # Dla zalogowanych użytkowników, przekierowanie do dashboardu
        return redirect(url_for('main.dashboard'))
    
    # Pokaż publiczne dashboardy jako przykłady
    sample_dashboards = Dashboard.query.filter_by(is_public=True).limit(3).all()
    
    return render_template(
        'main/index.html',
        title='Dashboard Analytics - Zaawansowane wizualizacje danych',
        sample_dashboards=sample_dashboards
    )