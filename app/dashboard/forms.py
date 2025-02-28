from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, BooleanField, IntegerField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Length, Optional, ValidationError, NumberRange


class DashboardForm(FlaskForm):
    """Formularz do tworzenia i edycji dashboardu"""
    title = StringField('Tytuł', validators=[DataRequired(), Length(min=3, max=120)])
    description = TextAreaField('Opis', validators=[Optional(), Length(max=500)])
    layout = SelectField('Układ', choices=[
        ('grid', 'Siatka'),
        ('flex', 'Elastyczny'),
        ('free', 'Dowolny')
    ])
    theme = SelectField('Motyw', choices=[
        ('light', 'Jasny'),
        ('dark', 'Ciemny'),
        ('blue', 'Niebieski'),
        ('green', 'Zielony'),
        ('orange', 'Pomarańczowy'),
        ('purple', 'Fioletowy')
    ])
    is_public = BooleanField('Publiczny dashboard')
    submit = SubmitField('Zapisz dashboard')


class WidgetForm(FlaskForm):
    """Formularz do tworzenia i edycji widgetu"""
    title = StringField('Tytuł', validators=[DataRequired(), Length(min=2, max=120)])
    widget_type = SelectField('Typ widgetu', choices=[
        ('chart', 'Wykres'),
        ('table', 'Tabela'),
        ('metric', 'Metryka'),
        ('text', 'Tekst')
    ])
    chart_type = SelectField('Typ wykresu', choices=[
        ('bar', 'Słupkowy'),
        ('line', 'Liniowy'),
        ('pie', 'Kołowy'),
        ('scatter', 'Punktowy'),
        ('area', 'Obszarowy'),
        ('heatmap', 'Mapa ciepła'),
        ('radar', 'Radarowy')
    ])
    width = IntegerField('Szerokość', validators=[
        DataRequired(),
        NumberRange(min=1, max=12, message='Szerokość musi być między 1 a 12')
    ], default=4)
    height = IntegerField('Wysokość', validators=[
        DataRequired(),
        NumberRange(min=1, max=12, message='Wysokość musi być między 1 a 12')
    ], default=4)
    data_source_id = SelectField('Źródło danych', coerce=int, validators=[DataRequired()])
    query = TextAreaField('Zapytanie', validators=[DataRequired()])
    settings = HiddenField('Ustawienia', default='{}')
    submit = SubmitField('Zapisz widget')
    
    def validate_chart_type(form, field):
        """Walidacja typu wykresu - wymagane tylko dla widgetów typu chart"""
        if form.widget_type.data == 'chart' and not field.data:
            raise ValidationError('Typ wykresu jest wymagany dla widgetów typu chart')


class DataSourceForm(FlaskForm):
    """Formularz do dodawania i edycji źródeł danych"""
    name = StringField('Nazwa', validators=[DataRequired(), Length(min=3, max=120)])
    description = TextAreaField('Opis', validators=[Optional(), Length(max=500)])
    source_type = SelectField('Typ źródła', choices=[
        ('database', 'Baza danych'),
        ('file', 'Plik'),
        ('api', 'API')
    ])
    refresh_rate = IntegerField('Częstotliwość odświeżania (min)', validators=[
        Optional(),
        NumberRange(min=0, max=1440, message='Częstotliwość musi być między 0 a 1440 minut')
    ], default=0)
    
    # Pola dla źródeł typu database
    db_type = SelectField('Typ bazy danych', choices=[
        ('postgresql', 'PostgreSQL'),
        ('mysql', 'MySQL'),
        ('sqlite', 'SQLite'),
        ('mssql', 'Microsoft SQL Server')
    ])
    db_host = StringField('Host', validators=[Optional(), Length(max=120)])
    db_port = IntegerField('Port', validators=[Optional()])
    db_name = StringField('Nazwa bazy', validators=[Optional(), Length(max=120)])
    db_username = StringField('Użytkownik', validators=[Optional(), Length(max=120)])
    db_password = StringField('Hasło', validators=[Optional(), Length(max=120)])
    
    # Pola dla źródeł typu file
    file_path = StringField('Ścieżka do pliku', validators=[Optional(), Length(max=255)])
    file_type = SelectField('Typ pliku', choices=[
        ('csv', 'CSV'),
        ('xlsx', 'Excel'),
        ('json', 'JSON')
    ])
    
    # Pola dla źródeł typu API
    api_url = StringField('URL API', validators=[Optional(), Length(max=500)])
    api_auth_type = SelectField('Typ autoryzacji', choices=[
        ('none', 'Brak'),
        ('basic', 'Basic Auth'),
        ('bearer', 'Bearer Token'),
        ('apikey', 'API Key')
    ])
    api_headers = TextAreaField('Nagłówki (JSON)', validators=[Optional()])
    api_params = TextAreaField('Parametry (JSON)', validators=[Optional()])
    
    submit = SubmitField('Zapisz źródło danych')
    
    def validate(self):
        """Walidacja formularza w zależności od typu źródła"""
        if not FlaskForm.validate(self):
            return False
        
        if self.source_type.data == 'database':
            if not self.db_type.data:
                self.db_type.errors = ['Typ bazy danych jest wymagany']
                return False
            if not self.db_name.data:
                self.db_name.errors = ['Nazwa bazy danych jest wymagana']
                return False
        
        elif self.source_type.data == 'file':
            if not self.file_path.data:
                self.file_path.errors = ['Ścieżka do pliku jest wymagana']
                return False
            if not self.file_type.data:
                self.file_type.errors = ['Typ pliku jest wymagany']
                return False
        
        elif self.source_type.data == 'api':
            if not self.api_url.data:
                self.api_url.errors = ['URL API jest wymagany']
                return False
        
        return True


class ShareDashboardForm(FlaskForm):
    """Formularz do udostępniania dashboardu innym użytkownikom"""
    email = StringField('Email użytkownika', validators=[DataRequired()])
    permission_level = SelectField('Poziom uprawnień', choices=[
        ('view', 'Tylko podgląd'),
        ('edit', 'Edycja'),
        ('admin', 'Administrator')
    ])
    submit = SubmitField('Udostępnij')