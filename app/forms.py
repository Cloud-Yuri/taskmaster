from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField, DateField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired()])
    submit = SubmitField('Entrar')

class RegistroForm(FlaskForm):
    nome = StringField('Nome', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    senha = PasswordField('Senha', validators=[DataRequired(), Length(min=6)])
    confirmar_senha = PasswordField('Confirmar Senha', validators=[DataRequired(), EqualTo('senha')])
    submit = SubmitField('Cadastrar')

class TarefaForm(FlaskForm):
    titulo = StringField('Título', validators=[DataRequired(), Length(max=200)])
    descricao = TextAreaField('Descrição', validators=[Optional()])
    categoria = SelectField('Categoria', choices=[
        ('Pessoal', 'Pessoal'),
        ('Trabalho', 'Trabalho'),
        ('Estudos', 'Estudos'),
        ('Saúde', 'Saúde'),
        ('Financeiro', 'Financeiro'),
        ('Outros', 'Outros')
    ], default='Pessoal')
    prioridade = SelectField('Prioridade', choices=[
        ('1', '🔴 Alta'),
        ('2', '🟡 Média'),
        ('3', '🟢 Baixa')
    ], default='2')
    data_vencimento = DateField('Data de Vencimento', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Salvar Tarefa')