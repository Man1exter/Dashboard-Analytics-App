from flask import render_template, flash, redirect, url_for, request, jsonify, current_app
from flask_login import login_required, current_user
from app import db, cache
from app.dashboard import bp
from app.dashboard.models import Dashboard, Widget, DataSource
from app.dashboard.forms import DashboardForm, WidgetForm, DataSourceForm, ShareDashboardForm
from app.auth.models import User
from werkzeug.exceptions import NotFound, Forbidden
from sqlalchemy import desc
import json


@bp.route('/')
@login_required
def index():
    """Wyświetla listę dashboardów użytkownika"""
    dashboards = Dashboard.query.filter_by(user_id=current_user.id).order_by(desc(Dashboard.updated_at)).all()
    
    # Pobierz również dashboardy udostępnione użytkownikowi
    shared_dashboards = Dashboard.query.join(
        Dashboard.collaborators
    ).filter_by(user_id=current_user.id).all()
    
    return render_template(
        'dashboard/index.html',
        title='Moje Dashboardy',
        dashboards=dashboards,
        shared_dashboards=shared_dashboards
    )


@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_dashboard():
    """Tworzenie nowego dashboardu"""
    form = DashboardForm()
    
    if form.validate_on_submit():
        dashboard = Dashboard(
            title=form.title.data,
            description=form.description.data,
            layout=form.layout.data,
            theme=form.theme.data,
            is_public=form.is_public.data,
            user_id=current_user.id
        )
        db.session.add(dashboard)
        db.session.commit()
        
        flash('Dashboard został utworzony pomyślnie.', 'success')
        return redirect(url_for('dashboard.view', dashboard_id=dashboard.id))
    
    return render_template(
        'dashboard/create.html',
        title='Nowy Dashboard',
        form=form,
        themes=current_app.config['DASHBOARD_THEMES']
    )


@bp.route('/<int:dashboard_id>')
@login_required
def view(dashboard_id):
    """Wyświetla dashboard z widgetami"""
    dashboard = Dashboard.query.get_or_404(dashboard_id)
    
    # Sprawdź uprawnienia dostępu
    if dashboard.user_id != current_user.id and not dashboard.is_public:
        # Sprawdź czy użytkownik jest współpracownikiem
        collaborator = next((c for c in dashboard.collaborators if c.user_id == current_user.id), None)
        if not collaborator:
            flash('Nie masz uprawnień do wyświetlenia tego dashboardu.', 'danger')
            return redirect(url_for('dashboard.index'))
    
    # Pobierz widgety z cache lub bazy danych
    cache_key = f'dashboard_widgets_{dashboard_id}'
    widgets = cache.get(cache_key)
    
    if not widgets:
        widgets = Widget.query.filter_by(dashboard_id=dashboard_id).all()
        cache.set(cache_key, widgets, timeout=60)  # Cache na 1 minutę
    
    return render_template(
        'dashboard/view.html',
        title=dashboard.title,
        dashboard=dashboard,
        widgets=widgets
    )


@bp.route('/<int:dashboard_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_dashboard(dashboard_id):
    """Edycja dashboardu"""
    dashboard = Dashboard.query.get_or_404(dashboard_id)
    
    # Sprawdź uprawnienia
    if dashboard.user_id != current_user.id:
        collaborator = next((c for c in dashboard.collaborators if c.user_id == current_user.id), None)
        if not collaborator or collaborator.permission_level not in ['edit', 'admin']:
            flash('Nie masz uprawnień do edycji tego dashboardu.', 'danger')
            return redirect(url_for('dashboard.view', dashboard_id=dashboard_id))
    
    form = DashboardForm(obj=dashboard)
    
    if form.validate_on_submit():
        dashboard.title = form.title.data
        dashboard.description = form.description.data
        dashboard.layout = form.layout.data
        dashboard.theme = form.theme.data
        dashboard.is_public = form.is_public.data
        
        db.session.commit()
        
        # Wyczyść cache
        cache.delete(f'dashboard_widgets_{dashboard_id}')
        
        flash('Dashboard został zaktualizowany.', 'success')
        return redirect(url_for('dashboard.view', dashboard_id=dashboard_id))
    
    return render_template(
        'dashboard/edit.html',
        title=f'Edycja - {dashboard.title}',
        form=form,
        dashboard=dashboard,
        themes=current_app.config['DASHBOARD_THEMES']
    )


@bp.route('/<int:dashboard_id>/delete', methods=['POST'])
@login_required
def delete_dashboard(dashboard_id):
    """Usuwanie dashboardu"""
    dashboard = Dashboard.query.get_or_404(dashboard_id)
    
    # Sprawdź uprawnienia
    if dashboard.user_id != current_user.id:
        return jsonify({'success': False, 'message': 'Brak uprawnień do usunięcia dashboardu'}), 403
    
    db.session.delete(dashboard)
    db.session.commit()
    
    # Wyczyść cache
    cache.delete(f'dashboard_widgets_{dashboard_id}')
    
    flash('Dashboard został usunięty.', 'success')
    return redirect(url_for('dashboard.index'))


@bp.route('/<int:dashboard_id>/widget/add', methods=['GET', 'POST'])
@login_required
def add_widget(dashboard_id):
    """Dodawanie nowego widgetu do dashboardu"""
    dashboard = Dashboard.query.get_or_404(dashboard_id)
    
    # Sprawdź uprawnienia
    if dashboard.user_id != current_user.id:
        collaborator = next((c for c in dashboard.collaborators if c.user_id == current_user.id), None)
        if not collaborator or collaborator.permission_level not in ['edit', 'admin']:
            flash('Nie masz uprawnień do dodawania widgetów do tego dashboardu.', 'danger')
            return redirect(url_for('dashboard.view', dashboard_id=dashboard_id))
    
    # Sprawdź limity
    if dashboard.widget_count >= current_app.config.get('MAX_WIDGETS_PER_DASHBOARD', 20):
        flash('Osiągnięto maksymalną liczbę widgetów dla tego dashboardu.', 'warning')
        return redirect(url_for('dashboard.view', dashboard_id=dashboard_id))
    
    form = WidgetForm()
    
    # Pobierz źródła danych dla selectfield
    data_sources = DataSource.query.filter_by(user_id=current_user.id, is_active=True).all()
    form.data_source_id.choices = [(ds.id, ds.name) for ds in data_sources]
    
    if form.validate_on_submit():
        widget = Widget(
            title=form.title.data,
            widget_type=form.widget_type.data,
            chart_type=form.chart_type.data if form.widget_type.data == 'chart' else None,
            width=form.width.data,
            height=form.height.data,
            query=form.query.data,
            settings=json.loads(form.settings.data),
            dashboard_id=dashboard_id,
            data_source_id=form.data_source_id.data
        )
        
        db.session.add(widget)
        db.session.commit()
        
        # Wyczyść cache
        cache.delete(f'dashboard_widgets_{dashboard_id}')
        
        flash('Widget został dodany pomyślnie.', 'success')
        return redirect(url_for('dashboard.view', dashboard_id=dashboard_id))
    
    return render_template(
        'dashboard/widget_add.html',
        title='Dodaj widget',
        form=form,
        dashboard=dashboard
    )


@bp.route('/widget/<int:widget_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_widget(widget_id):
    """Edycja widgetu"""
    widget = Widget.query.get_or_404(widget_id)
    dashboard = Dashboard.query.get_or_404(widget.dashboard_id)
    
    # Sprawdź uprawnienia
    if dashboard.user_id != current_user.id:
        collaborator = next((c for c in dashboard.collaborators if c.user_id == current_user.id), None)
        if not collaborator or collaborator.permission_level not in ['edit', 'admin']:
            flash('Nie masz uprawnień do edycji widgetów tego dashboardu.', 'danger')
            return redirect(url_for('dashboard.view', dashboard_id=dashboard.id))
    
    form = WidgetForm(obj=widget)
    
    # Pobierz źródła danych dla selectfield
    data_sources = DataSource.query.filter_by(user_id=current_user.id, is_active=True).all()
    form.data_source_id.choices = [(ds.id, ds.name) for ds in data_sources]
    
    # Ustawienie początkowych wartości
    if request.method == 'GET':
        form.settings.data = json.dumps(widget.settings)
    
    if form.validate_on_submit():
        widget.title = form.title.data
        widget.widget_type = form.widget_type.data
        widget.chart_type = form.chart_type.data if form.widget_type.data == 'chart' else None
        widget.width = form.width.data
        widget.height = form.height.data
        widget.query = form.query.data
        widget.settings = json.loads(form.settings.data)
        widget.data_source_id = form.data_source_id.data
        
        db.session.commit()
        
        # Wyczyść cache
        cache.delete(f'dashboard_widgets_{dashboard.id}')
        
        flash('Widget został zaktualizowany.', 'success')
        return redirect(url_for('dashboard.view', dashboard_id=dashboard.id))
    
    return render_template(
        'dashboard/widget_edit.html',
        title='Edycja widgetu',
        form=form,
        widget=widget,
        dashboard=dashboard
    )


@bp.route('/widget/<int:widget_id>/delete', methods=['POST'])
@login_required
def delete_widget(widget_id):
    """Usuwanie widgetu"""
    widget = Widget.query.get_or_404(widget_id)
    dashboard = Dashboard.query.get_or_404(widget.dashboard_id)
    
    # Sprawdź uprawnienia
    if dashboard.user_id != current_user.id:
        collaborator = next((c for c in dashboard.collaborators if c.user_id == current_user.id), None)
        if not collaborator or collaborator.permission_level not in ['edit', 'admin']:
            return jsonify({'success': False, 'message': 'Brak uprawnień do usunięcia widgetu'}), 403
    
    db.session.delete(widget)
    db.session.commit()
    
    # Wyczyść cache
    cache.delete(f'dashboard_widgets_{dashboard.id}')
    
    flash('Widget został usunięty.', 'success')
    return redirect(url_for('dashboard.view', dashboard_id=dashboard.id))


@bp.route('/<int:dashboard_id>/share', methods=['GET', 'POST'])
@login_required
def share_dashboard(dashboard_id):
    """Udostępnianie dashboardu innym użytkownikom"""
    dashboard = Dashboard.query.get_or_404(dashboard_id)
    
    # Sprawdź uprawnienia
    if dashboard.user_id != current_user.id:
        flash('Tylko właściciel dashboardu może go udostępniać.', 'danger')
        return redirect(url_for('dashboard.view', dashboard_id=dashboard_id))
    
    form = ShareDashboardForm()
    
    if form.validate_on_submit():
        # Znajdź użytkownika po emailu
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash(f'Użytkownik z adresem {form.email.data} nie istnieje.', 'danger')
            return redirect(url_for('dashboard.share_dashboard', dashboard_id=dashboard_id))
        
        # Sprawdź czy dashboard jest już udostępniony temu użytkownikowi
        existing = next((c for c in dashboard.collaborators if c.user_id == user.id), None)
        if existing:
            existing.permission_level = form.permission_level.data
            flash(f'Zaktualizowano uprawnienia dla {user.email}.', 'success')
        else:
            # Dodaj współpracownika
            from app.dashboard.models import DashboardCollaborator
            collaborator = DashboardCollaborator(
                dashboard_id=dashboard_id,
                user_id=user.id,
                permission_level=form.permission_level.data
            )
            db.session.add(collaborator)
            flash(f'Dashboard został udostępniony użytkownikowi {user.email}.', 'success')
        
        db.session.commit()
        return redirect(url_for('dashboard.share_dashboard', dashboard_id=dashboard_id))
    
    # Pobierz listę współpracowników
    collaborators = []
    for collab in dashboard.collaborators:
        user = User.query.get(collab.user_id)
        collaborators.append({
            'id': collab.id,
            'user': user,
            'permission_level': collab.permission_level
        })
    
    return render_template(
        'dashboard/share.html',
        title=f'Udostępnij - {dashboard.title}',
        form=form,
        dashboard=dashboard,
        collaborators=collaborators
    )


@bp.route('/data_sources')
@login_required
def data_sources():
    """Wyświetla listę źródeł danych użytkownika"""
    sources = DataSource.query.filter_by(user_id=current_user.id).order_by(DataSource.name).all()
    return render_template(
        'dashboard/data_sources.html',
        title='Źródła danych',
        data_sources=sources
    )


@bp.route('/data_source/add', methods=['GET', 'POST'])
@login_required
def add_data_source():
    """Dodaje nowe źródło danych"""
    form = DataSourceForm()
    
    if form.validate_on_submit():
        connection_details = {}
        
        # Budowanie connection_details na podstawie typu źródła
        if form.source_type.data == 'database':
            connection_details = {
                'host': form.db_host.data,
                'port': form.db_port.data,
                'database': form.db_name.data,
                'username': form.db_username.data,
                'password': form.db_password.data,
                'type': form.db_type.data
            }
        elif form.source_type.data == 'file':
            connection_details = {
                'file_path': form.file_path.data,
                'file_type': form.file_type.data
            }
        elif form.source_type.data == 'api':
            connection_details = {
                'url': form.api_url.data,
                'auth_type': form.api_auth_type.data,
                'headers': form.api_headers.data,
                'params': form.api_params.data
            }
        
        data_source = DataSource(
            name=form.name.data,
            description=form.description.data,
            source_type=form.source_type.data,
            connection_details=connection_details,
            refresh_rate=form.refresh_rate.data,
            user_id=current_user.id
        )
        
        db.session.add(data_source)
        db.session.commit()
        
        flash('Źródło danych zostało dodane pomyślnie.', 'success')
        return redirect(url_for('dashboard.data_sources'))
    
    return render_template(
        'dashboard/data_source_add.html',
        title='Dodaj źródło danych',
        form=form
    )