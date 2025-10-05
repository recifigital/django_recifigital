from django.db import models
from django.contrib.auth.hashers import make_password, check_password

class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True)
    nome = models.TextField(max_length=255)
    senha = models.CharField(max_length=255)
    situacao = models.IntegerField(default=0)  # 0 = aguardando, 1 = ativo, 2 = ADM

    def save(self, *args, **kwargs):
        if not self.pk or not self.senha.startswith('pbkdf2_'):
            self.senha = make_password(self.senha)
        super().save(*args, **kwargs)

    def verificar_senha(self, senha_digitada):
        return check_password(senha_digitada, self.senha)

    def __str__(self):
        return self.nome
