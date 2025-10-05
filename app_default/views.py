from django.shortcuts import render, redirect
from .models import Usuario
from django.shortcuts import get_object_or_404
from django.contrib.sessions.models import Session
from django.utils import timezone
from functools import wraps
from django.contrib import messages

def registrar(request):
    mensagem_erro = None

    if request.method == 'POST':
        usuario_nome = request.POST.get('nome')
        usuario_senha = request.POST.get('senha')

        if usuario_nome and usuario_senha:
            if Usuario.objects.filter(nome=usuario_nome).exists():
                mensagem_erro = "Este nome de usuário já está em uso. Escolha outro."
            else:
                novo_usuario = Usuario(
                    nome=usuario_nome,
                    senha=usuario_senha,
                    situacao=0  # aguardando aprovação
                )
                novo_usuario.save()
                # Mensagem informativa
                return render(request, 'mlp.recifigital/aguardando_aprovacao.html')

    return render(request, 'mlp.recifigital/registrar.html', {'erro': mensagem_erro})

def login(request):
    erro_nome = None
    erro_senha = None

    if request.method == 'POST':
        usuario_nome = request.POST.get('nome')
        usuario_senha = request.POST.get('senha')

        try:
            usuario = Usuario.objects.get(nome=usuario_nome)

            # Primeiro verifica se a senha está correta
            if usuario.verificar_senha(usuario_senha):
                # Depois verifica se o usuário foi aprovado
                if usuario.situacao == 0:
                    erro_nome = "Sua conta ainda está aguardando aprovação do administrador."
                else:
                    # Login bem-sucedido
                    request.session['usuario_id'] = usuario.id_usuario
                    request.session['usuario_nome'] = usuario.nome
                    request.session['usuario_situacao'] = usuario.situacao

                    # Redireciona ADM para a página de usuários
                    if usuario.situacao == 2:
                        return redirect('listagem_usuarios')
                    else:
                        return redirect('home')
            else:
                erro_senha = "Senha incorreta."

        except Usuario.DoesNotExist:
            erro_nome = "Usuário não encontrado."

    return render(request, 'mlp.recifigital/login.html', {
        'erro_nome': erro_nome,
        'erro_senha': erro_senha
    })

def login_obrigatorio(func):
    def wrapper(request, *args, **kwargs):
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            return redirect('login')  # não está logado

        try:
            usuario = Usuario.objects.get(id_usuario=usuario_id)
        except Usuario.DoesNotExist:
            return redirect('login')  # usuário não existe

        # permite apenas situacao 1 (ativo) ou 2 (ADM)
        if usuario.situacao not in [1, 2]:
            return redirect('login')  # ainda não aprovado ou bloqueado

        return func(request, *args, **kwargs)
    return wrapper

def adm_obrigatorio(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        usuario_id = request.session.get('usuario_id')
        if not usuario_id:
            return redirect('login')
        
        usuario = Usuario.objects.get(id_usuario=usuario_id)
        if usuario.situacao != 2:  # Apenas ADM
            return redirect('home')  # Ou outra página de acesso negado
        return func(request, *args, **kwargs)
    return wrapper

@adm_obrigatorio
def lista_usuarios(request):
    usuarios_lista = Usuario.objects.all()
    return render(request, 'mlp.recifigital/usuarios.html', {'usuarios': usuarios_lista})

@login_obrigatorio
def tornar_admin(request, usuario_id):
    # Somente quem tem situação 2 (admin) pode promover
    if request.session.get('usuario_situacao') != 2:
        messages.error(request, "Você não tem permissão para isso.")
        return redirect('listagem_usuarios')

    usuario = get_object_or_404(Usuario, id_usuario=usuario_id)
    erro = None

    if request.method == "POST":
        senha = request.POST.get("senha")
        usuario_logado = Usuario.objects.get(id_usuario=request.session['usuario_id'])

        # Verifica a senha do usuário logado
        if usuario_logado.verificar_senha(senha):
            usuario.situacao = 2
            usuario.save()
            messages.success(request, f"{usuario.nome} agora é administrador.")
            return redirect('listagem_usuarios')
        else:
            erro = "Senha incorreta. Tente novamente."

    return render(request, 'mlp.recifigital/tornar_admin.html', {'usuario': usuario, 'erro': erro})

@login_obrigatorio
def aprovar_usuario(request, id_usuario):
    usuario = get_object_or_404(Usuario, id_usuario=id_usuario)
    
    # Apenas ADM (situacao 2) pode aprovar
    usuario_atual = Usuario.objects.get(id_usuario=request.session['usuario_id'])
    if usuario_atual.situacao == 2 and usuario.situacao == 0:
        usuario.situacao = 1
        usuario.save()
    
    return redirect('listagem_usuarios')

@login_obrigatorio
def excluir_usuario(request, usuario_id):
    usuario_a_excluir = get_object_or_404(Usuario, id_usuario=usuario_id)
    usuario_logado_id = request.session.get('usuario_id')
    usuario_logado = get_object_or_404(Usuario, id_usuario=usuario_logado_id)
    erro = None

    if request.method == 'POST':
        senha_confirmacao = request.POST.get('senha')
        
        if usuario_logado.verificar_senha(senha_confirmacao):
            # Excluir todas as sessões do usuário a ser deletado
            all_sessions = Session.objects.filter(expire_date__gte=timezone.now())
            for session in all_sessions:
                data = session.get_decoded()
                if data.get('usuario_id') == usuario_a_excluir.id_usuario:
                    session.delete()

            # Exclui o usuário
            usuario_a_excluir.delete()
            return redirect('listagem_usuarios')
        else:
            erro = "Senha incorreta. Exclusão não realizada."

    return render(request, 'mlp.recifigital/excluir_usuario.html', {
        'usuario': usuario_a_excluir,
        'erro': erro
    })

@login_obrigatorio
def home(request):
    usuario_nome = request.session.get('usuario_nome', 'Visitante')
    return render(request, 'mlp.recifigital/home.html', {'usuario_nome': usuario_nome})

@login_obrigatorio
def escritorio(request):
    return render(request,'mlp.recifigital/escritorio.html')

@login_obrigatorio
def projetos(request):
    return render(request,'mlp.recifigital/projetos.html')

@login_obrigatorio
def recrutamento(request):
    return render(request,'mlp.recifigital/recrutamento.html')

@login_obrigatorio
def noticias(request):
    return render(request,'mlp.recifigital/noticias.html')

@login_obrigatorio
def privacidade(request):
    return render(request,'mlp.recifigital/privacidade.html')

def logout(request):
    request.session.flush()
    return redirect('login')
