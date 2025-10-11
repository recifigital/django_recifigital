# projeto_mlp/middleware.py
from django.core.exceptions import PermissionDenied
from app_default.models import Usuario

class AdminPermissionMiddleware:
    """
    Bloqueia acesso ao /admin/ para usuários não logados ou sem situacao=2.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/admin/'):
            usuario_id = request.session.get('usuario_id')
            if not usuario_id:
                raise PermissionDenied  # não logado

            try:
                usuario = Usuario.objects.get(id_usuario=usuario_id)
            except Usuario.DoesNotExist:
                raise PermissionDenied  # usuário não existe

            if usuario.situacao != 2:
                raise PermissionDenied  # não é ADM

        response = self.get_response(request)
        return response
