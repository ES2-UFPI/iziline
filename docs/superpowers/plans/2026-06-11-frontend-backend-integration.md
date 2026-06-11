# Frontend ↔ Backend Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remover os mocks do frontend e fazer as telas de Cadastrar viagem e Buscar caronas conversarem com a API Django, com autenticação de sessão (registro/login) e estimativa de custo real.

**Architecture:** Backend ganha um app `accounts` (HackSoft) com auth de sessão, CORS via `django-cors-headers`, e um endpoint de estimativa que reusa o cálculo de rateio. No frontend, os services existentes (`createTrip`, `calculateTripCosts`, `searchRides`) são o ponto de costura: troca-se o interior por chamadas reais, mantendo as assinaturas. Login é a porta de entrada via um `AuthProvider`.

**Tech Stack:** Backend: Django 6 + DRF + django-cors-headers (testes via `manage.py test`). Frontend: Vite + React 19 + axios (validação por smoke test manual).

**Convenção:** comandos backend rodam com `/Users/eduardomelo/Documents/iziline/backend/.venv/bin/python` a partir de `/Users/eduardomelo/Documents/iziline-integration/backend/src`. Comandos frontend a partir de `/Users/eduardomelo/Documents/iziline-integration/frontend`. Branch: `feat/frontend-backend-integration`.

---

## File Structure

```
backend/
├── requirements.txt                         MODIFICAR (+ django-cors-headers)
└── src/
    ├── core/
    │   ├── settings.py                       MODIFICAR (CORS/CSRF, apps, middleware, tira BasicAuth)
    │   └── urls.py                            MODIFICAR (+ /api/auth/)
    ├── accounts/                              NOVO app
    │   ├── apps.py, __init__.py, migrations/
    │   ├── services.py                        user_register()
    │   ├── serializers.py                     Register/Login/User
    │   ├── apis.py                            Register/Login/Logout/Me
    │   ├── urls.py
    │   └── tests.py
    └── trip/
        ├── services.py                        MODIFICAR (fare_breakdown)
        ├── serializers.py                     MODIFICAR (FareEstimateSerializer)
        ├── apis.py                            MODIFICAR (FareEstimateApi)
        ├── urls.py                            MODIFICAR (+ fare-estimate/)
        └── tests.py                           MODIFICAR (401→403, testes fare-estimate)
    └── booking/tests.py                       MODIFICAR (401→403)
frontend/
├── .env                                       NOVO (VITE_API_BASE_URL)
└── src/
    ├── travel/service/apiClient.ts            MODIFICAR (interceptor CSRF)
    ├── travel/service/serviceApi.ts           MODIFICAR (createTrip real)
    ├── travel/service/costService.ts          MODIFICAR (fare-estimate real)
    ├── carona/service/rideService.ts          MODIFICAR (search real + mapeamento)
    ├── types/trip.ts                           MODIFICAR (TripCostEstimate)
    ├── types/ride.ts                           MODIFICAR (carModel opcional)
    ├── travel/pages/NewTripPage/NewTripPage.tsx  MODIFICAR (resumo de custos)
    ├── carona/pages/RideSearchPage/RideSearchPage.tsx MODIFICAR (carModel guard)
    ├── auth/service/authService.ts            NOVO
    ├── auth/AuthContext.tsx                    NOVO
    ├── auth/pages/LoginPage/LoginPage.tsx      NOVO
    ├── auth/pages/LoginPage/LoginPage.css      NOVO
    ├── App.tsx                                 MODIFICAR (gate de auth + logout)
    └── main.tsx                                MODIFICAR (AuthProvider)
```

---

## Task 1: Backend — CORS, CSRF e remoção do BasicAuth

**Files:** `backend/requirements.txt`, `backend/src/core/settings.py`, `backend/src/trip/tests.py`, `backend/src/booking/tests.py`

- [ ] **Step 1: Instalar django-cors-headers**

Run:
```bash
cd /Users/eduardomelo/Documents/iziline-integration/backend
/Users/eduardomelo/Documents/iziline/backend/.venv/bin/pip install django-cors-headers
/Users/eduardomelo/Documents/iziline/backend/.venv/bin/pip freeze > requirements.txt
```
Expected: `django-cors-headers` aparece no requirements.txt.

- [ ] **Step 2: Ajustar os testes de auth (401 → 403)**

Sem `BasicAuthentication`, requisições sem credenciais retornam 403. Em `backend/src/trip/tests.py` e `backend/src/booking/tests.py`, troque as 6 asserções `self.assertEqual(response.status_code, 401)` por `self.assertEqual(response.status_code, 403)` (linhas que testam acesso sem autenticação: trip 252/281/366; booking 186/325/353).

- [ ] **Step 3: Rodar os testes para confirmar a falha**

Run:
```bash
cd /Users/eduardomelo/Documents/iziline-integration/backend/src
/Users/eduardomelo/Documents/iziline/backend/.venv/bin/python manage.py test trip booking 2>&1 | tail -15
```
Expected: FALHAM os testes "requires_authentication" (ainda retornam 401 porque o BasicAuth não foi removido). Isso confirma que o ajuste depende do Step 4.

- [ ] **Step 4: Configurar settings (CORS, CSRF, apps, middleware, auth)**

Em `backend/src/core/settings.py`:

(a) Em `INSTALLED_APPS`, adicione `'corsheaders'` (antes de `'rest_framework'`). **Não** adicione `'accounts'` aqui — esse app só é criado na Task 2 (adicioná-lo agora quebraria o `manage.py test`):
```python
    'corsheaders',
    'rest_framework',
    'trip',
    'booking',
    'chat',
]
```

(b) Em `MIDDLEWARE`, adicione `corsheaders.middleware.CorsMiddleware` logo após `SecurityMiddleware`:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

(c) Substitua o bloco `REST_FRAMEWORK` inteiro (remove o `BasicAuthentication`):
```python
# Django REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}

# CORS / CSRF para o frontend Vite (localhost:5173)
CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]
CORS_ALLOW_CREDENTIALS = True
CSRF_TRUSTED_ORIGINS = ["http://localhost:5173"]
```

- [ ] **Step 5: Rodar os testes para confirmar que passam**

Run:
```bash
cd /Users/eduardomelo/Documents/iziline-integration/backend/src
/Users/eduardomelo/Documents/iziline/backend/.venv/bin/python manage.py test trip booking 2>&1 | tail -6
```
Expected: todos passam (os "requires_authentication" agora veem 403).

- [ ] **Step 6: Commit**

```bash
cd /Users/eduardomelo/Documents/iziline-integration
git add backend/requirements.txt backend/src/core/settings.py backend/src/trip/tests.py backend/src/booking/tests.py
git commit -m "feat: configurar CORS/CSRF e remover BasicAuth (auth de sessao para o SPA)"
```

---

## Task 2: Backend — App accounts (registro/login/logout/me)

**Files:** `backend/src/accounts/` (novo app), `backend/src/core/urls.py`

> **Nota:** o app NÃO pode se chamar `auth` (colide com o app_label de `django.contrib.auth`). Nome: `accounts`. As URLs ficam em `/api/auth/`.

- [ ] **Step 1: Criar o app**

Run:
```bash
cd /Users/eduardomelo/Documents/iziline-integration/backend/src
/Users/eduardomelo/Documents/iziline/backend/.venv/bin/python manage.py startapp accounts
rm accounts/models.py accounts/views.py accounts/admin.py accounts/tests.py
```
(O `accounts` não tem model próprio — usa o User do Django. Removemos os arquivos não usados; recriamos `tests.py` no Step 2.)

- [ ] **Step 2: Escrever os testes que falham**

Crie `backend/src/accounts/tests.py`:
```python
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):
    def test_register_creates_and_authenticates(self):
        r = self.client.post(
            reverse("auth-register"),
            {"username": "ana", "password": "secret123", "first_name": "Ana", "last_name": "Silva"},
            format="json",
        )
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["username"], "ana")
        self.assertEqual(r.data["name"], "Ana Silva")
        self.assertTrue(User.objects.filter(username="ana").exists())
        me = self.client.get(reverse("auth-me"))
        self.assertEqual(me.data["username"], "ana")

    def test_register_duplicate_username(self):
        User.objects.create_user(username="ana", password="x")
        r = self.client.post(
            reverse("auth-register"), {"username": "ana", "password": "secret123"}, format="json"
        )
        self.assertEqual(r.status_code, 400)

    def test_login_valid(self):
        User.objects.create_user(username="ana", password="secret123")
        r = self.client.post(
            reverse("auth-login"), {"username": "ana", "password": "secret123"}, format="json"
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["username"], "ana")

    def test_login_invalid(self):
        User.objects.create_user(username="ana", password="secret123")
        r = self.client.post(
            reverse("auth-login"), {"username": "ana", "password": "errada"}, format="json"
        )
        self.assertEqual(r.status_code, 400)

    def test_me_anonymous_returns_null(self):
        r = self.client.get(reverse("auth-me"))
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(r.data)

    def test_logout(self):
        User.objects.create_user(username="ana", password="secret123")
        self.client.login(username="ana", password="secret123")
        r = self.client.post(reverse("auth-logout"))
        self.assertEqual(r.status_code, 204)
        self.assertIsNone(self.client.get(reverse("auth-me")).data)
```

- [ ] **Step 3: Rodar para confirmar a falha**

Run:
```bash
cd /Users/eduardomelo/Documents/iziline-integration/backend/src
/Users/eduardomelo/Documents/iziline/backend/.venv/bin/python manage.py test accounts -v 2
```
Expected: FAIL — `NoReverseMatch` para `auth-register` (urls não existem).

- [ ] **Step 4: Implementar service, serializers, apis, urls**

Crie `backend/src/accounts/services.py`:
```python
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
```

Crie `backend/src/accounts/serializers.py`:
```python
from rest_framework import serializers


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=6)
    first_name = serializers.CharField(required=False, allow_blank=True, default="")
    last_name = serializers.CharField(required=False, allow_blank=True, default="")


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.get_full_name() or obj.get_username()
```

Crie `backend/src/accounts/apis.py`:
```python
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.serializers import LoginSerializer, RegisterSerializer, UserSerializer
from accounts.services import user_register


class RegisterApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = user_register(**serializer.validated_data)
        login(request, user)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


class LoginApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, **serializer.validated_data)
        if user is None:
            return Response({"detail": "Credenciais inválidas."}, status=status.HTTP_400_BAD_REQUEST)
        login(request, user)
        return Response(UserSerializer(user).data)


class LogoutApi(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


@method_decorator(ensure_csrf_cookie, name="get")
class MeApi(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        if request.user.is_authenticated:
            return Response(UserSerializer(request.user).data)
        return Response(None)
```

Crie `backend/src/accounts/urls.py`:
```python
from django.urls import path

from accounts.apis import LoginApi, LogoutApi, MeApi, RegisterApi

urlpatterns = [
    path("register/", RegisterApi.as_view(), name="auth-register"),
    path("login/", LoginApi.as_view(), name="auth-login"),
    path("logout/", LogoutApi.as_view(), name="auth-logout"),
    path("me/", MeApi.as_view(), name="auth-me"),
]
```

Em `backend/src/core/settings.py`, adicione `'accounts'` ao final de `INSTALLED_APPS` (agora o app existe):
```python
    'chat',
    'accounts',
]
```

Em `backend/src/core/urls.py`, adicione o include (abaixo do de bookings):
```python
    path('api/auth/', include('accounts.urls')),
```

- [ ] **Step 5: Rodar para confirmar que passa**

Run:
```bash
cd /Users/eduardomelo/Documents/iziline-integration/backend/src
/Users/eduardomelo/Documents/iziline/backend/.venv/bin/python manage.py test accounts -v 2
```
Expected: PASS (6 testes).

- [ ] **Step 6: Commit**

```bash
cd /Users/eduardomelo/Documents/iziline-integration
git add backend/src/accounts backend/src/core/urls.py backend/src/core/settings.py
git commit -m "feat: app accounts com auth de sessao (register/login/logout/me)"
```

---

## Task 3: Backend — Endpoint de estimativa de custo (fare-estimate)

**Files:** `backend/src/trip/services.py`, `backend/src/trip/serializers.py`, `backend/src/trip/apis.py`, `backend/src/trip/urls.py`, `backend/src/trip/tests.py`

- [ ] **Step 1: Escrever os testes que falham**

Acrescente ao topo de `backend/src/trip/tests.py` (junto aos imports) `from django.urls import reverse` se ainda não houver, e adicione ao final:
```python
class FareEstimateApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", password="x")

    def test_requires_authentication(self):
        r = self.client.get(reverse("trip-fare-estimate"),
                             {"origin": "Teresina", "destination": "Parnaiba", "seats_available": 2})
        self.assertEqual(r.status_code, 403)

    def test_returns_breakdown(self):
        self.client.force_authenticate(self.user)
        r = self.client.get(reverse("trip-fare-estimate"),
                             {"origin": "Teresina", "destination": "Parnaiba", "seats_available": 2})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["distance_km"], 339)
        self.assertEqual(r.data["occupants"], 3)
        self.assertEqual(r.data["per_person"], "33.90")
        self.assertEqual(r.data["total_cost"], "101.70")

    def test_invalid_seats_returns_400(self):
        self.client.force_authenticate(self.user)
        r = self.client.get(reverse("trip-fare-estimate"),
                             {"origin": "A", "destination": "B", "seats_available": 0})
        self.assertEqual(r.status_code, 400)
```

- [ ] **Step 2: Rodar para confirmar a falha**

Run:
```bash
cd /Users/eduardomelo/Documents/iziline-integration/backend/src
/Users/eduardomelo/Documents/iziline/backend/.venv/bin/python manage.py test trip.tests.FareEstimateApiTests -v 2
```
Expected: FAIL — `NoReverseMatch` para `trip-fare-estimate`.

- [ ] **Step 3: Refatorar calculate_fare expondo a decomposição**

Em `backend/src/trip/services.py`, substitua a função `calculate_fare` por estas duas (mantendo o comportamento de `calculate_fare`):
```python
def fare_breakdown(*, origin, destination, seats_available):
    """Decomposição do rateio (mock). Fonte única de cálculo."""
    if seats_available < 1:
        raise ValidationError({"seats_available": "Deve haver ao menos 1 vaga."})
    key = frozenset({_normalize_city(origin), _normalize_city(destination)})
    distance_km = _KNOWN_DISTANCES_KM.get(key, _DEFAULT_DISTANCE_KM)
    total_cost = (Decimal(distance_km) * _COST_PER_KM).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    occupants = seats_available + 1
    per_person = (Decimal(distance_km) * _COST_PER_KM / Decimal(occupants)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    return {
        "distance_km": distance_km,
        "cost_per_km": _COST_PER_KM,
        "total_cost": total_cost,
        "occupants": occupants,
        "per_person": per_person,
    }


def calculate_fare(*, origin, destination, seats_available):
    """Rateio por pessoa (mock). Usa fare_breakdown como fonte única."""
    return fare_breakdown(
        origin=origin, destination=destination, seats_available=seats_available
    )["per_person"]
```

- [ ] **Step 4: Adicionar o serializer de filtros**

Em `backend/src/trip/serializers.py`, adicione ao final:
```python
class FareEstimateSerializer(serializers.Serializer):
    origin = serializers.CharField()
    destination = serializers.CharField()
    seats_available = serializers.IntegerField(min_value=1)
```

- [ ] **Step 5: Adicionar a view**

Em `backend/src/trip/apis.py`, adicione o import do `fare_breakdown` e do serializer, e a view:
```python
from trip.services import fare_breakdown  # junto ao import existente de trip.services
from trip.serializers import FareEstimateSerializer  # junto aos demais serializers


class FareEstimateApi(APIView):
    def get(self, request):
        filters = FareEstimateSerializer(data=request.query_params)
        filters.is_valid(raise_exception=True)
        data = fare_breakdown(**filters.validated_data)
        return Response({
            "distance_km": data["distance_km"],
            "cost_per_km": str(data["cost_per_km"]),
            "total_cost": str(data["total_cost"]),
            "occupants": data["occupants"],
            "per_person": str(data["per_person"]),
        })
```

- [ ] **Step 6: Registrar a rota**

Em `backend/src/trip/urls.py`, adicione (antes da rota `<int:trip_id>/`):
```python
from trip.apis import FareEstimateApi  # junto ao import existente

# dentro de urlpatterns, antes de "<int:trip_id>/":
    path("fare-estimate/", FareEstimateApi.as_view(), name="trip-fare-estimate"),
```

- [ ] **Step 7: Rodar para confirmar que passa**

Run:
```bash
cd /Users/eduardomelo/Documents/iziline-integration/backend/src
/Users/eduardomelo/Documents/iziline/backend/.venv/bin/python manage.py test trip -v 1 2>&1 | tail -6
```
Expected: PASS (todos os testes de trip, incl. FareEstimateApiTests).

- [ ] **Step 8: Commit**

```bash
cd /Users/eduardomelo/Documents/iziline-integration
git add backend/src/trip
git commit -m "feat: endpoint GET /api/trips/fare-estimate/ (decomposicao do rateio)"
```

---

## Task 4: Frontend — apiClient com CSRF e .env

**Files:** `frontend/.env`, `frontend/src/travel/service/apiClient.ts`

- [ ] **Step 1: Criar o .env**

Crie `frontend/.env`:
```
VITE_API_BASE_URL=http://localhost:8000
```

- [ ] **Step 2: Reescrever o apiClient com interceptor de CSRF**

Substitua `frontend/src/travel/service/apiClient.ts` por:
```ts
import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "";

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp("(^|; )" + name + "=([^;]*)"));
  return match ? decodeURIComponent(match[2]) : null;
}

apiClient.interceptors.request.use((config) => {
  const method = (config.method ?? "get").toLowerCase();
  if (["post", "put", "patch", "delete"].includes(method)) {
    const token = getCookie("csrftoken");
    if (token) {
      config.headers = config.headers ?? {};
      (config.headers as Record<string, string>)["X-CSRFToken"] = token;
    }
  }
  return config;
});
```

- [ ] **Step 3: Verificar build**

Run:
```bash
cd /Users/eduardomelo/Documents/iziline-integration/frontend
npm install
npx tsc -b
```
Expected: sem erros de TypeScript.

- [ ] **Step 4: Commit**

```bash
cd /Users/eduardomelo/Documents/iziline-integration
git add frontend/.env frontend/src/travel/service/apiClient.ts
git commit -m "feat(front): apiClient com baseURL via env e header CSRF"
```

---

## Task 5: Frontend — authService, AuthProvider e tela de Login

**Files:** `frontend/src/auth/service/authService.ts`, `frontend/src/auth/AuthContext.tsx`, `frontend/src/auth/pages/LoginPage/LoginPage.tsx`, `frontend/src/auth/pages/LoginPage/LoginPage.css`, `frontend/src/main.tsx`, `frontend/src/App.tsx`

- [ ] **Step 1: authService**

Crie `frontend/src/auth/service/authService.ts`:
```ts
import { apiClient } from "../../travel/service/apiClient";

export type AuthUser = { id: number; username: string; name: string };

export type RegisterInput = {
  username: string;
  password: string;
  first_name?: string;
  last_name?: string;
};

export async function register(input: RegisterInput): Promise<AuthUser> {
  const { data } = await apiClient.post<AuthUser>("/api/auth/register/", input);
  return data;
}

export async function login(username: string, password: string): Promise<AuthUser> {
  const { data } = await apiClient.post<AuthUser>("/api/auth/login/", { username, password });
  return data;
}

export async function logout(): Promise<void> {
  await apiClient.post("/api/auth/logout/");
}

export async function me(): Promise<AuthUser | null> {
  const { data } = await apiClient.get<AuthUser | null>("/api/auth/me/");
  return data ?? null;
}
```

- [ ] **Step 2: AuthContext**

Crie `frontend/src/auth/AuthContext.tsx`:
```tsx
import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import {
  login as apiLogin,
  logout as apiLogout,
  me as apiMe,
  register as apiRegister,
  type AuthUser,
  type RegisterInput,
} from "./service/authService";

type AuthState = {
  user: AuthUser | null;
  loading: boolean;
  login: (username: string, password: string) => Promise<void>;
  register: (input: RegisterInput) => Promise<void>;
  logout: () => Promise<void>;
};

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    apiMe()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  async function login(username: string, password: string) {
    setUser(await apiLogin(username, password));
  }

  async function register(input: RegisterInput) {
    setUser(await apiRegister(input));
  }

  async function logout() {
    await apiLogout();
    setUser(null);
  }

  return (
    <AuthContext.Provider value={{ user, loading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth deve ser usado dentro de AuthProvider");
  return ctx;
}
```

- [ ] **Step 3: Tela de Login/Registro (identidade visual existente)**

Crie `frontend/src/auth/pages/LoginPage/LoginPage.css`:
```css
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: var(--bg);
  padding: 24px;
}

.login-card {
  width: 100%;
  max-width: 380px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 16px;
  box-shadow: var(--shadow);
  padding: 32px;
}

.login-card h1 {
  margin: 0 0 4px;
  color: var(--text-h);
  font: 600 22px/1.2 var(--heading);
}

.login-card p.subtitle {
  margin: 0 0 24px;
  color: var(--muted);
}

.login-card form {
  display: grid;
  gap: 16px;
}

.login-card button.primary {
  background: var(--accent);
  color: #fff;
  border: 0;
  border-radius: 10px;
  padding: 12px;
  font-weight: 600;
  cursor: pointer;
}

.login-card button.primary:hover {
  background: var(--accent-hover);
}

.login-card button.primary:disabled {
  opacity: 0.6;
  cursor: default;
}

.login-card .toggle {
  margin-top: 16px;
  text-align: center;
  color: var(--text);
}

.login-card .toggle button {
  background: none;
  border: 0;
  color: var(--accent);
  cursor: pointer;
  font-weight: 600;
}

.login-card .form-error {
  color: #b91c1c;
  font-size: 14px;
}
```

Crie `frontend/src/auth/pages/LoginPage/LoginPage.tsx`:
```tsx
import { useState } from "react";
import { FormField } from "../../../components/FormField/FormField";
import { useAuth } from "../../AuthContext";
import "./LoginPage.css";

type Mode = "login" | "register";

function extractError(err: unknown): string {
  const anyErr = err as { response?: { data?: Record<string, unknown> } };
  const data = anyErr?.response?.data;
  if (data) {
    const first = Object.values(data)[0];
    if (Array.isArray(first)) return String(first[0]);
    if (typeof first === "string") return first;
  }
  return "Não foi possível concluir. Tente novamente.";
}

export function LoginPage() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<Mode>("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      if (mode === "login") {
        await login(username, password);
      } else {
        const [first_name, ...rest] = name.trim().split(" ");
        await register({
          username,
          password,
          first_name: first_name ?? "",
          last_name: rest.join(" "),
        });
      }
    } catch (err) {
      setError(extractError(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>iziline</h1>
        <p className="subtitle">
          {mode === "login" ? "Entre na sua conta" : "Crie sua conta"}
        </p>
        <form onSubmit={handleSubmit}>
          {mode === "register" && (
            <FormField
              id="name"
              label="Nome"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Seu nome"
            />
          )}
          <FormField
            id="username"
            label="Usuário"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <FormField
            id="password"
            label="Senha"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {error && <span className="form-error">{error}</span>}
          <button type="submit" className="primary" disabled={submitting}>
            {submitting ? "Aguarde..." : mode === "login" ? "Entrar" : "Criar conta"}
          </button>
        </form>
        <div className="toggle">
          {mode === "login" ? "Não tem conta?" : "Já tem conta?"}{" "}
          <button
            type="button"
            onClick={() => {
              setError("");
              setMode(mode === "login" ? "register" : "login");
            }}
          >
            {mode === "login" ? "Criar conta" : "Entrar"}
          </button>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: Envolver o app no AuthProvider**

Substitua `frontend/src/main.tsx` por:
```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import { AuthProvider } from './auth/AuthContext'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <AuthProvider>
      <App />
    </AuthProvider>
  </StrictMode>,
)
```

- [ ] **Step 5: Gate de auth no App.tsx**

Em `frontend/src/App.tsx`, adicione os imports e o gate. No topo:
```tsx
import { useAuth } from './auth/AuthContext'
import { LoginPage } from './auth/pages/LoginPage/LoginPage'
```
Logo no início do componente `App()` (antes do `return` existente), adicione:
```tsx
  const { user, loading, logout } = useAuth()

  if (loading) {
    return <div style={{ padding: 32 }}>Carregando...</div>
  }

  if (!user) {
    return <LoginPage />
  }
```
E dentro do `<nav className="app-navigation" ...>`, adicione ao final um botão de sair:
```tsx
        <button
          type="button"
          className="app-navigation__item"
          onClick={() => { void logout() }}
          style={{ marginLeft: 'auto' }}
        >
          Sair ({user.name})
        </button>
```

- [ ] **Step 6: Verificar build**

Run:
```bash
cd /Users/eduardomelo/Documents/iziline-integration/frontend
npx tsc -b
```
Expected: sem erros de TypeScript.

- [ ] **Step 7: Commit**

```bash
cd /Users/eduardomelo/Documents/iziline-integration
git add frontend/src/auth frontend/src/main.tsx frontend/src/App.tsx
git commit -m "feat(front): auth de sessao (authService, AuthProvider, tela de login)"
```

---

## Task 6: Frontend — createTrip e searchRides reais

**Files:** `frontend/src/travel/service/serviceApi.ts`, `frontend/src/carona/service/rideService.ts`, `frontend/src/types/ride.ts`, `frontend/src/carona/pages/RideSearchPage/RideSearchPage.tsx`

- [ ] **Step 1: createTrip chamando a API**

Em `frontend/src/travel/service/serviceApi.ts`: adicione o import do apiClient no topo e substitua o corpo de `createTrip` (mantendo `buildDepartureAt`, `buildCreateTripPayload` e `ApiError`):
```ts
import { apiClient } from "./apiClient";
// ... (mantém os tipos e ApiError existentes)

export async function createTrip(input: CreateTripInput): Promise<TripResponse> {
  const payload = buildCreateTripPayload(input);
  try {
    const { data } = await apiClient.post<TripResponse>("/api/trips/", payload);
    return data;
  } catch (err) {
    const anyErr = err as { response?: { status?: number; data?: unknown } };
    throw new ApiError(
      "Não foi possível criar a viagem.",
      anyErr?.response?.status ?? 0,
      anyErr?.response?.data,
    );
  }
}
```

- [ ] **Step 2: Tornar carModel opcional**

Em `frontend/src/types/ride.ts`, mude `carModel: string;` para `carModel?: string;`.

- [ ] **Step 3: searchRides chamando a API + mapeamento**

Substitua o conteúdo de `frontend/src/carona/service/rideService.ts` por:
```ts
import { apiClient } from "../../travel/service/apiClient";
import type { RideSearchFilters, RideSearchResult } from "../../../types/ride";

type ApiTrip = {
  id: number;
  driver_name: string;
  origin: string;
  destination: string;
  departure_at: string;
  seats_available: number;
  price: string;
};

function mapTrip(t: ApiTrip): RideSearchResult {
  return {
    id: t.id,
    driverName: t.driver_name,
    origin: t.origin,
    destination: t.destination,
    departureAt: t.departure_at,
    seatsAvailable: t.seats_available,
    price: t.price,
  };
}

export async function searchRides(
  filters: RideSearchFilters
): Promise<RideSearchResult[]> {
  const params: Record<string, string> = {};
  if (filters.origin.trim()) params.origin = filters.origin.trim();
  if (filters.destination.trim()) params.destination = filters.destination.trim();
  if (filters.date) params.date = filters.date;

  const { data } = await apiClient.get<{ results: ApiTrip[] }>("/api/trips/", { params });
  return (data.results ?? []).map(mapTrip);
}
```

- [ ] **Step 4: Guardar a renderização do carModel**

Em `frontend/src/carona/pages/RideSearchPage/RideSearchPage.tsx`, na linha que renderiza `<span>{ride.carModel}</span>`, troque por renderização condicional:
```tsx
        {ride.carModel && <span>{ride.carModel}</span>}
```

- [ ] **Step 5: Verificar build**

Run:
```bash
cd /Users/eduardomelo/Documents/iziline-integration/frontend
npx tsc -b
```
Expected: sem erros de TypeScript.

- [ ] **Step 6: Commit**

```bash
cd /Users/eduardomelo/Documents/iziline-integration
git add frontend/src/travel/service/serviceApi.ts frontend/src/carona/service/rideService.ts frontend/src/types/ride.ts frontend/src/carona/pages/RideSearchPage/RideSearchPage.tsx
git commit -m "feat(front): createTrip e searchRides consumindo a API real"
```

---

## Task 7: Frontend — estimativa de custo real (resumo)

**Files:** `frontend/src/types/trip.ts`, `frontend/src/travel/service/costService.ts`, `frontend/src/travel/pages/NewTripPage/NewTripPage.tsx`

- [ ] **Step 1: Novo tipo TripCostEstimate**

Em `frontend/src/types/trip.ts`, substitua `TripCostBreakdownItem` e `TripCostEstimate` por:
```ts
export type TripCostEstimate = {
  distanceInKm: number;
  costPerKm: string;
  totalCost: string;
  occupants: number;
  perPersonCost: string;
};
```
(Remova o tipo `TripCostBreakdownItem`, que não será mais usado.)

- [ ] **Step 2: costService chamando o fare-estimate**

Substitua o conteúdo de `frontend/src/travel/service/costService.ts` por:
```ts
import { apiClient } from "./apiClient";
import type { CreateTripInput, TripCostEstimate } from "../../types/trip";

type FareEstimateResponse = {
  distance_km: number;
  cost_per_km: string;
  total_cost: string;
  occupants: number;
  per_person: string;
};

export async function calculateTripCosts(
  input: CreateTripInput
): Promise<TripCostEstimate> {
  const { data } = await apiClient.get<FareEstimateResponse>(
    "/api/trips/fare-estimate/",
    {
      params: {
        origin: input.origin.trim(),
        destination: input.destination.trim(),
        seats_available: input.availableSeats,
      },
    }
  );
  return {
    distanceInKm: data.distance_km,
    costPerKm: data.cost_per_km,
    totalCost: data.total_cost,
    occupants: data.occupants,
    perPersonCost: data.per_person,
  };
}
```

- [ ] **Step 3: Atualizar o resumo de custos no NewTripPage**

Em `frontend/src/travel/pages/NewTripPage/NewTripPage.tsx`, o sub-componente que recebe `costEstimate: TripCostEstimate` (por volta das linhas 210–295) renderiza campos que não existem mais (`fuelEfficiencyKmPerLiter`, `fuelPricePerLiter`, `breakdown`, `serviceFeeRate`). Substitua o corpo desse resumo para usar os novos campos. Renderize:
```tsx
        <p>
          Distância estimada: <strong>{costEstimate.distanceInKm} km</strong>
        </p>
        <p>
          Custo por km: <strong>R$ {costEstimate.costPerKm}</strong>
        </p>
        <p>
          Ocupantes (motorista + passageiros): <strong>{costEstimate.occupants}</strong>
        </p>
        <p>
          Custo total: <strong>R$ {costEstimate.totalCost}</strong>
        </p>
        <p>
          Valor por pessoa: <strong>R$ {costEstimate.perPersonCost}</strong>
        </p>
```
Remova as referências aos campos antigos (e às funções de formatação que dependiam deles, como `formatFuelEfficiency`, `formatFuelPrice`, `percentFormatter`, e o `.map` do `breakdown`), e quaisquer imports/variáveis que ficarem sem uso. O objetivo: o resumo passa a mostrar distância, custo por km, ocupantes, total e valor por pessoa, todos vindos do backend.

- [ ] **Step 4: Verificar build (sem variáveis órfãs)**

Run:
```bash
cd /Users/eduardomelo/Documents/iziline-integration/frontend
npx tsc -b
```
Expected: sem erros de TypeScript (corrija qualquer "declared but never used" removendo o código morto do resumo antigo).

- [ ] **Step 5: Commit**

```bash
cd /Users/eduardomelo/Documents/iziline-integration
git add frontend/src/types/trip.ts frontend/src/travel/service/costService.ts frontend/src/travel/pages/NewTripPage/NewTripPage.tsx
git commit -m "feat(front): resumo de custos consumindo /api/trips/fare-estimate/"
```

---

## Task 8: Smoke test de ponta a ponta

**Files:** (nenhum)

- [ ] **Step 1: Suíte de backend verde**

Run:
```bash
cd /Users/eduardomelo/Documents/iziline-integration/backend/src
/Users/eduardomelo/Documents/iziline/backend/.venv/bin/python manage.py test -v 1 2>&1 | tail -6
/Users/eduardomelo/Documents/iziline/backend/.venv/bin/python manage.py check
```
Expected: todos os testes passam; `System check identified no issues`.

- [ ] **Step 2: Migrar e subir o backend**

Run (em background ou outro terminal):
```bash
cd /Users/eduardomelo/Documents/iziline-integration/backend/src
/Users/eduardomelo/Documents/iziline/backend/.venv/bin/python manage.py migrate
/Users/eduardomelo/Documents/iziline/backend/.venv/bin/python manage.py runserver 127.0.0.1:8000
```

- [ ] **Step 3: Subir o frontend**

Run (outro terminal):
```bash
cd /Users/eduardomelo/Documents/iziline-integration/frontend
npm run dev
```
Abra http://localhost:5173.

- [ ] **Step 4: Percorrer o fluxo real (sem mocks)**

Verifique no navegador:
1. A tela de **Login** aparece (não há sessão).
2. **Criar conta** (nome, usuário, senha) → entra no app.
3. **Cadastrar viagem** → o resumo de custos mostra distância/custo-km/total/por-pessoa **vindos do backend**; confirmar cria a viagem (`201`).
4. **Buscar caronas** → a viagem recém-criada aparece nos resultados (origem/destino/data/preço reais; sem campo de carro).
5. **Sair** → volta para a tela de login.

Confirme no terminal do backend que as requisições `POST /api/trips/`, `GET /api/trips/fare-estimate/`, `GET /api/trips/` e `/api/auth/*` retornam 2xx.

- [ ] **Step 5: Commit final (se houver ajustes)**

```bash
cd /Users/eduardomelo/Documents/iziline-integration
git add -A && git commit -m "chore: ajustes do smoke test da integracao" --allow-empty
```

---

## Mapa de cobertura (spec → tasks)

| Requisito da spec | Task |
|-------------------|------|
| CORS + CSRF | Task 1 |
| Remover BasicAuth (401→403) | Task 1 |
| App accounts (register/login/logout/me) | Task 2 |
| fare-estimate (decomposição A+) | Task 3 |
| apiClient + CSRF + env | Task 4 |
| authService + AuthProvider + tela de login | Task 5 |
| createTrip + searchRides reais + mapeamento + carModel | Task 6 |
| costService real + resumo de custos | Task 7 |
| Smoke test de ponta a ponta | Task 8 |

## Fora de escopo
- Autocomplete real de endereços (mantém mock em `locationService`).
- Telas de Reserva e Agenda no frontend.
- JWT, deploy/produção, PostgreSQL.
