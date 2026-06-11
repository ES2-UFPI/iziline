from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError

User = get_user_model()


def user_register(*, username, password, first_name="", last_name=""):
    if User.objects.filter(username=username).exists():
        raise ValidationError({"username": "Este nome de usuário já está em uso."})
    user = User(username=username, first_name=first_name, last_name=last_name)
    user.set_password(password)
    user.save()
    return user
