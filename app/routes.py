from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import Usuario, Tarefa
from app.forms import LoginForm, RegistroForm, TarefaForm
from datetime import datetime, date

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(email=form.email.data).first()
        if usuario and usuario.check_senha(form.senha.data):
            login_user(usuario)
            next_page = request.args.get('next')
            flash(f'Bem-vindo, {usuario.nome}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
        else:
            flash('Email ou senha incorretos.', 'danger')
    
    return render_template('login.html', form=form)

@bp.route('/registrar', methods=['GET', 'POST'])
def registrar():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = RegistroForm()
    if form.validate_on_submit():
        if Usuario.query.filter_by(email=form.email.data).first():
            flash('Este email já está cadastrado.', 'danger')
            return redirect(url_for('main.registrar'))
        
        usuario = Usuario(nome=form.nome.data, email=form.email.data)
        usuario.set_senha(form.senha.data)
        db.session.add(usuario)
        db.session.commit()
        
        flash('Cadastro realizado! Faça login.', 'success')
        return redirect(url_for('main.login'))
    
    return render_template('register.html', form=form)

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Você saiu da conta.', 'info')
    return redirect(url_for('main.login'))

@bp.route('/dashboard')
@login_required
def dashboard():
    filtro = request.args.get('filtro', 'todas')
    hoje = date.today()
    
    query = Tarefa.query.filter_by(usuario_id=current_user.id)
    
    if filtro == 'hoje':
        query = query.filter_by(data_vencimento=hoje)
    elif filtro == 'semana':
        from datetime import timedelta
        semana = hoje + timedelta(days=7)
        query = query.filter(Tarefa.data_vencimento.between(hoje, semana))
    elif filtro == 'atrasadas':
        query = query.filter(Tarefa.data_vencimento < hoje, Tarefa.status != 'concluida')
    elif filtro == 'concluidas':
        query = query.filter_by(status='concluida')
    else:
        query = query.filter(Tarefa.status != 'concluida')
    
    tarefas = query.order_by(Tarefa.prioridade, Tarefa.data_vencimento).all()
    
    # Estatísticas
    stats = {
        'total': Tarefa.query.filter_by(usuario_id=current_user.id).count(),
        'pendentes': Tarefa.query.filter_by(usuario_id=current_user.id, status='pendente').count(),
        'concluidas': Tarefa.query.filter_by(usuario_id=current_user.id, status='concluida').count(),
        'atrasadas': Tarefa.query.filter(Tarefa.usuario_id == current_user.id, 
                                        Tarefa.data_vencimento < hoje, 
                                        Tarefa.status != 'concluida').count()
    }
    
    return render_template('dashboard.html', tarefas=tarefas, stats=stats, filtro=filtro, hoje=hoje)

@bp.route('/tarefa/nova', methods=['GET', 'POST'])
@login_required
def nova_tarefa():
    form = TarefaForm()
    if form.validate_on_submit():
        tarefa = Tarefa(
            titulo=form.titulo.data,
            descricao=form.descricao.data,
            categoria=form.categoria.data,
            prioridade=int(form.prioridade.data),
            data_vencimento=form.data_vencimento.data,
            usuario_id=current_user.id
        )
        db.session.add(tarefa)
        db.session.commit()
        flash('Tarefa criada!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('tarefa_form.html', form=form, titulo='Nova Tarefa')

@bp.route('/tarefa/editar/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_tarefa(id):
    tarefa = Tarefa.query.get_or_404(id)
    if tarefa.usuario_id != current_user.id:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = TarefaForm(obj=tarefa)
    if form.validate_on_submit():
        tarefa.titulo = form.titulo.data
        tarefa.descricao = form.descricao.data
        tarefa.categoria = form.categoria.data
        tarefa.prioridade = int(form.prioridade.data)
        tarefa.data_vencimento = form.data_vencimento.data
        db.session.commit()
        flash('Tarefa atualizada!', 'success')
        return redirect(url_for('main.dashboard'))
    
    return render_template('tarefa_form.html', form=form, titulo='Editar Tarefa')

@bp.route('/tarefa/concluir/<int:id>')
@login_required
def concluir_tarefa(id):
    tarefa = Tarefa.query.get_or_404(id)
    if tarefa.usuario_id != current_user.id:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    tarefa.status = 'concluida'
    tarefa.concluido_em = datetime.utcnow()
    db.session.commit()
    flash('Tarefa concluída! Parabéns! 🎉', 'success')
    return redirect(url_for('main.dashboard'))

@bp.route('/tarefa/excluir/<int:id>')
@login_required
def excluir_tarefa(id):
    tarefa = Tarefa.query.get_or_404(id)
    if tarefa.usuario_id != current_user.id:
        flash('Acesso negado.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    db.session.delete(tarefa)
    db.session.commit()
    flash('Tarefa excluída.', 'info')
    return redirect(url_for('main.dashboard'))