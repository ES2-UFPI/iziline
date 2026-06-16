# Models, regras de negocio e persistencia

Responsavel: `EdsonDaSilvaLJ`

## Tecnologia abordada

Este tutorial mostra como modelar dados no Django, criar migrations e isolar uma regra de negocio em uma funcao de service. O exemplo usa uma viagem com origem, destino, data e vagas.

## Instalacao e configuracao minima

Requisitos:

- Backend Django configurado.
- Banco local padrao do Django ou outro banco definido em `settings.py`.
- Ambiente virtual ativo.

Comandos principais:

```bash
cd backend/src
python manage.py makemigrations
python manage.py migrate
python manage.py shell
```

## Exemplo funcional

Model de exemplo:

```py
from django.conf import settings
from django.db import models


class Trip(models.Model):
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_trips',
    )
    origin = models.CharField(max_length=120)
    destination = models.CharField(max_length=120)
    date = models.DateTimeField()
    seats_available = models.PositiveIntegerField()
    is_cancelled = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.origin} -> {self.destination}'
```

Service de exemplo:

```py
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Trip


def create_trip(*, driver, origin, destination, date, seats_available):
    if date <= timezone.now():
        raise ValidationError('A data da viagem deve ser futura.')

    if seats_available < 1:
        raise ValidationError('A viagem deve ter pelo menos uma vaga.')

    return Trip.objects.create(
        driver=driver,
        origin=origin,
        destination=destination,
        date=date,
        seats_available=seats_available,
    )
```

Teste rapido no shell:

```py
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.utils import timezone

from trip.services import create_trip

User = get_user_model()
driver = User.objects.create_user(username='motorista', password='teste123')

trip = create_trip(
    driver=driver,
    origin='Teresina',
    destination='Parnaiba',
    date=timezone.now() + timedelta(days=1),
    seats_available=3,
)

print(trip.id, trip.origin, trip.destination)
```

## O que demonstrar no video

- Explicar o papel de `models.py`.
- Rodar `makemigrations` e `migrate`.
- Mostrar uma regra de negocio em service.
- Criar uma viagem pelo shell ou por teste automatizado.
- Mostrar que os dados foram persistidos no banco local.

## Links oficiais

- Django models: https://docs.djangoproject.com/en/6.0/topics/db/models/
- Django migrations: https://docs.djangoproject.com/en/6.0/topics/migrations/
- Django queries: https://docs.djangoproject.com/en/6.0/topics/db/queries/
- Django validation: https://docs.djangoproject.com/en/6.0/ref/forms/validation/

