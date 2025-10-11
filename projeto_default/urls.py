from django.contrib import admin
from django.urls import path, include
from app_default import views
from django.shortcuts import render

def erro_404(request, exception):
    return render(request, '404.html', status=404)

def erro_403(request, exception):
    return render(request, '403.html', status=403)

urlpatterns = [
    # rota, view responsável, nome de referência
    # mlp.recifigital.com.br
    path('',views.home,name='home'),
    path('admin/', admin.site.urls),  
    path('registrar/',views.registrar,name='registrar'),
    path('login/',views.login,name='login'),
    path('logout/', views.logout, name='logout'),
    path('usuarios/',views.lista_usuarios,name='listagem_usuarios'),
    path('usuarios/excluir/<int:usuario_id>/', views.excluir_usuario, name='excluir_usuario'),
    path('usuarios/aprovar/<int:id_usuario>/', views.aprovar_usuario, name='aprovar_usuario'),
    path('usuarios/tornar_admin/<int:usuario_id>/', views.tornar_admin, name='tornar_admin'),
    path('escritorio/',views.escritorio,name='escritorio'),
    path('projetos/',views.projetos,name='projetos'),
    path('recrutamento/',views.recrutamento,name='recrutamento'),
    path('noticias/',views.noticias,name='noticias'),
    path('privacidade/',views.privacidade,name='privacidade'),
]

handler404 = erro_404
handler403 = erro_403