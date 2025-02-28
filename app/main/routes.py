from flask import render_template, redirect, url_for, request, current_app
from flask_login import current_user, login_required, logout_user
from app.main import bp
from app.dashboard.models import Dashboard
from sqlalchemy import desc
from app import db 

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


@bp.route('/dashboard')
@login_required
def dashboard():
    """Widok dashboardu dla zalogowanych użytkowników"""
    user_dashboards = Dashboard.query.filter_by(user_id=current_user.id).order_by(desc(Dashboard.created_at)).all()
    
    return render_template(
        'main/dashboard.html',
        title='Twój Dashboard',
        user_dashboards=user_dashboards
    )


@bp.route('/dashboard/<int:dashboard_id>')
@login_required
def view_dashboard(dashboard_id):
    """Widok pojedynczego dashboardu"""
    dashboard = Dashboard.query.get_or_404(dashboard_id)
    if dashboard.user_id != current_user.id and not dashboard.is_public:
        return redirect(url_for('main.index'))
    
    return render_template(
        'main/view_dashboard.html',
        title=dashboard.title,
        dashboard=dashboard
    )


@bp.route('/dashboard/new', methods=['GET', 'POST'])
@login_required
def new_dashboard():
    """Tworzenie nowego dashboardu"""
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        is_public = request.form.get('is_public') == 'on'
        
        new_dashboard = Dashboard(
            title=title,
            description=description,
            is_public=is_public,
            user_id=current_user.id
        )
        db.session.add(new_dashboard)
        db.session.commit()
        
        return redirect(url_for('main.dashboard'))
    
    return render_template(
        'main/new_dashboard.html',
        title='Nowy Dashboard'
    )


@bp.route('/dashboard/delete/<int:dashboard_id>', methods=['POST'])
@login_required
def delete_dashboard(dashboard_id):
    """Usuwanie dashboardu"""
    dashboard = Dashboard.query.get_or_404(dashboard_id)
    if dashboard.user_id != current_user.id:
        return redirect(url_for('main.index'))
    
    db.session.delete(dashboard)
    db.session.commit()
    
    return redirect(url_for('main.dashboard'))


@bp.route('/dashboard/edit/<int:dashboard_id>', methods=['GET', 'POST'])
@login_required
def edit_dashboard(dashboard_id):
    """Edycja istniejącego dashboardu"""
    dashboard = Dashboard.query.get_or_404(dashboard_id)
    if dashboard.user_id != current_user.id:
        return redirect(url_for('main.index'))
    
    if request.method == 'POST':
        dashboard.title = request.form.get('title')
        dashboard.description = request.form.get('description')
        dashboard.is_public = request.form.get('is_public') == 'on'
        db.session.commit()
        
        return redirect(url_for('main.view_dashboard', dashboard_id=dashboard.id))
    
    return render_template(
        'main/edit_dashboard.html',
        title='Edycja Dashboardu',
        dashboard=dashboard
    )


@bp.route('/public_dashboards')
def public_dashboards():
    """Widok publicznych dashboardów"""
    public_dashboards = Dashboard.query.filter_by(is_public=True).order_by(desc(Dashboard.created_at)).all()
    
    return render_template(
        'main/public_dashboards.html',
        title='Publiczne Dashboardy',
        public_dashboards=public_dashboards
    )


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Ustawienia użytkownika"""
    if request.method == 'POST':
        # Przetwarzanie formularza ustawień
        new_setting = request.form.get('new_setting')
        # Zaktualizuj ustawienia użytkownika w bazie danych
        current_user.settings = new_setting
        db.session.commit()
        return redirect(url_for('main.settings'))
    
    return render_template(
        'main/settings.html',
        title='Ustawienia użytkownika'
    )


@bp.route('/logout')
@login_required
def logout():
    """Wylogowanie użytkownika"""
    logout_user()
    return redirect(url_for('main.index'))