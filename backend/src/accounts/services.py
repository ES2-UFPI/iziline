from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError

User = get_user_model()

_USERNAME_TAKEN = "Este nome de usuário já está em uso."


def user_register(*, username, password, first_name="", last_name=""):
    with transaction.atomic():
        if User.objects.filter(username=username).exists():
            raise ValidationError({"username": _USERNAME_TAKEN})
        user = User(username=username, first_name=first_name, last_name=last_name)
        try:
            validate_password(password, user=user)
        except DjangoValidationError as exc:
            raise ValidationError({"password": exc.messages})
        user.set_password(password)
        try:
            user.save()
        except IntegrityError:
            raise ValidationError({"username": _USERNAME_TAKEN})
        return user
