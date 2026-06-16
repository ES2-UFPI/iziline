# APIs com Django REST Framework

Responsavel: `edumelocarv`

## Tecnologia abordada

Este tutorial apresenta a criacao de APIs com Django REST Framework. O foco e criar um endpoint simples para listar e cadastrar viagens usando serializer e view.

## Instalacao e configuracao minima

Requisitos:

- Python instalado.
- Ambiente virtual criado.
- Dependencias do backend instaladas.

Comandos principais:

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cd src
python manage.py migrate
python manage.py runserver
```

Em Linux/macOS, a ativacao do ambiente virtual muda para:

```bash
source .venv/bin/activate
```

## Exemplo funcional

Serializer de exemplo:

```py
from rest_framework import serializers


class TripSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    origin = serializers.CharField(max_length=120)
    destination = serializers.CharField(max_length=120)
    date = serializers.DateField()
    seats_available = serializers.IntegerField(min_value=1)
```

View de exemplo com armazenamento em memoria:

```py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import TripSerializer


TRIPS = []


class TripListCreateApi(APIView):
    def get(self, request):
        serializer = TripSerializer(TRIPS, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TripSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        trip = {
            'id': len(TRIPS) + 1,
            **serializer.validated_data,
        }
        TRIPS.append(trip)

        return Response(trip, status=status.HTTP_201_CREATED)
```

Rota de exemplo:

```py
from django.urls import path

from .apis import TripListCreateApi

urlpatterns = [
    path('trips/', TripListCreateApi.as_view(), name='trip-list-create'),
]
```

## O que demonstrar no video

- Criar ou explicar o ambiente virtual.
- Rodar migrations e servidor Django.
- Explicar serializer, view e URL.
- Testar `GET /api/trips/`.
- Testar `POST /api/trips/` com origem, destino, data e vagas.

## Links oficiais

- Django documentation: https://docs.djangoproject.com/en/6.0/
- Django REST Framework Quickstart: https://www.django-rest-framework.org/tutorial/quickstart/
- DRF Serializers: https://www.django-rest-framework.org/api-guide/serializers/
- DRF Views: https://www.django-rest-framework.org/api-guide/views/

