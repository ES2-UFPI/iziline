# Design — Integração Frontend ↔ Backend

**Data:** 2026-06-11
**Autor:** Eduardo Melo de Carvalho
**Branch:** `feat/frontend-backend-integration` (a partir de `main`)

## Objetivo

Remover os dados mockados do frontend e fazer as telas existentes — **Cadastrar
viagem** e **Buscar caronas** — se comunicarem de verdade com a API Django/DRF.
Adicionar autenticação de sessão (registro/login) como porta de entrada e um
endpoint de estimativa de custo. O autocomplete de endereço permanece mockado
(depende de API de mapas, fora de escopo).

## Contexto

- **Frontend:** app web Vite + React 19 + axios (não é React Native). Telas:
  `NewTripPage` e `RideSearchPage`, navegação simples por `window.history` em
  `App.tsx`. Services hoje retornam mock. Componente reutilizável `FormField` e
  paleta em `src/styles/global.css` (`--accent #2563eb`, `--surface`, `--border`…).
- **Backend:** Django 6 + DRF, apps `trip` e `booking` (estilo HackSoft). Todos
  os endpoints exigem `IsAuthenticated`. **Não há** endpoint de auth nem CORS.
- Frontend e backend convivem na branch `main`.

## Parte 1 — Backend (habilitação)

### 1.1 CORS + CSRF
- Adicionar `django-cors-headers` (em `requirements.txt`, `INSTALLED_APPS`,
  `MIDDLEWARE` no topo).
- `CORS_ALLOWED_ORIGINS = ["http://localhost:5173"]`, `CORS_ALLOW_CREDENTIALS = True`.
- `CSRF_TRUSTED_ORIGINS = ["http://localhost:5173"]`.
- `localhost:5173 ↔ localhost:8000` é *same-site* (mesmo registrable domain
  `localhost`), então o cookie de sessão `SameSite=Lax` é enviado entre as portas.

### 1.2 App `auth` (HackSoft flat) sob `/api/auth/`
Estrutura espelhando `trip`/`booking`: `services.py`, `serializers.py`, `apis.py`, `urls.py`.

- **`services.py`** — `user_register(*, username, password, first_name, last_name)`
  cria o `User` (com `set_password`), validando username único e senha não vazia.
- **`serializers.py`:**
  - `RegisterSerializer` — `username`, `password`, `first_name` (opcional), `last_name` (opcional).
  - `LoginSerializer` — `username`, `password`.
  - `UserSerializer` (saída) — `id`, `username`, `name` (get_full_name → username).
- **`apis.py`:**
  - `POST /api/auth/register/` (`AllowAny`) → cria conta, faz `login()` de sessão, retorna `201` + usuário.
  - `POST /api/auth/login/` (`AllowAny`) → `authenticate()` + `login()`; `200` + usuário, ou `400`.
  - `POST /api/auth/logout/` → `logout()`; `204`.
  - `GET /api/auth/me/` (`AllowAny`) → usuário logado ou `204`/`401`; também fixa o cookie CSRF (via `ensure_csrf_cookie`).

### 1.3 Ajuste de autenticação para SPA
- **Remover `BasicAuthentication`** do `DEFAULT_AUTHENTICATION_CLASSES` (evita o
  popup nativo de Basic Auth no navegador). Fica `SessionAuthentication`.
- Sem credenciais, o DRF passa a responder **403** (comportamento padrão de sessão).
  O frontend trata `401` e `403` como "não autenticado" e redireciona ao login.
- **Impacto nos testes:** os testes do `trip`/`booking` que esperavam `401` em
  requisição sem auth passam a esperar `403`. Ajustar esses testes.

### 1.4 Endpoint de estimativa de custo (A+)
- `GET /api/trips/fare-estimate/?origin=&destination=&seats_available=` (`IsAuthenticated`).
- Refatorar `calculate_fare` para expor a decomposição **sem duplicar lógica**:
  uma função `fare_breakdown(*, origin, destination, seats_available)` que retorna
  `{distance_km, cost_per_km, total_cost, occupants, per_person}`; `calculate_fare`
  passa a usá-la e retornar só o `per_person`.
- Valida os query params via serializer (`origin`, `destination`, `seats_available≥1`);
  param inválido → `400`.

## Parte 2 — Frontend (consumo real)

### 2.1 `apiClient`
- `.env` com `VITE_API_BASE_URL=http://localhost:8000`.
- `apiClient` (axios): `baseURL` do env, `withCredentials: true`, e um
  **interceptor de request** que, em métodos não seguros (POST/PUT/PATCH/DELETE),
  lê o cookie `csrftoken` e adiciona o header `X-CSRFToken`.

### 2.2 Autenticação no frontend
- `authService.ts`: `register()`, `login()`, `logout()`, `me()`.
- Estado de auth via contexto React (`AuthProvider`) com o usuário atual.
- No carregamento, chama `me()`; se não autenticado, renderiza a **tela de
  Login/Registro** antes do app. Logado, mostra a navegação atual + botão "Sair".
- **Tela de Login/Registro** reusa o componente `FormField` e as variáveis de
  `global.css` (mesma identidade visual): card centralizado, inputs do mesmo
  estilo, botão com `--accent`. Alterna entre "Entrar" e "Criar conta".

### 2.3 Substituir mocks por chamadas reais
| Service | Antes | Depois |
|---------|-------|--------|
| `serviceApi.createTrip` | objeto fake | `POST /api/trips/` |
| `costService.calculateTripCosts` | constantes fake | `GET /api/trips/fare-estimate/` |
| `rideService.searchRides` | fixtures | `GET /api/trips/` + mapeamento; sem `carModel` |
| `locationService.getPossibleAddresses` | mock | **mantém mock** |

### 2.4 Mapeamento de tipos
- Camada fina (ex.: em cada service) que converte a resposta da API
  (`driver_name`, `departure_at`, `seats_available`, `price`) para os tipos
  camelCase consumidos pelas telas (`driverName`, `departureAt`, `seatsAvailable`).
- `RideSearchResult` perde `carModel` (sem campo no backend) — remover da exibição.
- O resumo de custos (`TripCostEstimate`) passa a refletir a decomposição do
  backend: distância, custo por km, total, ocupantes, valor por pessoa — em vez
  de combustível/pedágio/taxa. Ajustar o componente de resumo e o tipo.

## Tratamento de erros
- `400` da API → mensagens de campo nos formulários (login, registro, viagem),
  aproveitando o `ApiError` já existente.
- `401`/`403` → desautentica e volta à tela de login.
- Erro de rede → mensagem amigável genérica.

## Testes

**Backend:**
- `auth`: registro cria usuário e autentica (`201`); login válido (`200`) e
  inválido (`400`); `me` logado vs anônimo; logout (`204`).
- `fare-estimate`: decomposição correta para rota conhecida e default; param
  inválido → `400`; sem auth → `403`.
- Ajustar os testes de `trip`/`booking` de `401` → `403`.

**Frontend:**
- O frontend não tem framework de teste hoje e adicionar um está fora do escopo
  (YAGNI). A validação do frontend é por **smoke test manual**: subir backend +
  frontend e percorrer o fluxo real — registrar/logar → cadastrar viagem (preço
  vindo do backend) → buscar a viagem criada → sair. O mapeamento de tipos e o
  envio de CSRF são exercitados nesse fluxo.

## Onde o trabalho vive
Branch `feat/frontend-backend-integration` (worktree em
`/Users/eduardomelo/Documents/iziline-integration`), a partir de `main`. PR → `dev`.

## Fora de escopo
- Autocomplete real de endereços (API de mapas).
- Telas de Reserva e Agenda no frontend.
- JWT (mantém sessão), deploy/produção, PostgreSQL.
