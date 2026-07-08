# Auditoria front/back depois do teste global com Docker

Este documento cobre somente mudanças e decisões feitas a partir do teste global com Docker.

## Contexto

O teste global foi feito com a aplicação rodando em Docker, com backend, frontend e banco reais. O frontend foi executado com `VITE_USE_MOCK=false`, então as telas testadas chamaram a API real.

## O que foi encontrado e alterado

1. A stack Docker de desenvolvimento não subia de forma completa.
   - Motivo: a compose dependia de `backend/src/.env.dev`, que não existia, e não declarava banco nem frontend.
   - Mudança: foi criado um ambiente Docker de dev com Postgres, backend e frontend, além de healthchecks e frontend apontando para a API real.

2. A tela de viagens do motorista tinha chamada de frontend sem endpoint correspondente.
   - Motivo: `listDriverTrips()` lançava erro no modo real porque não havia API de "minhas viagens como motorista".
   - Mudança: foi criado `GET /api/trips/mine/` e o frontend passou a consumir esse endpoint.

3. A suíte de testes de custo dependia de configuração externa.
   - Motivo: no Docker dev, `PRICE_PER_KM=0.50`; alguns testes esperavam `1.00`.
   - Mudança: os testes passaram a fixar `PRICE_PER_KM=1.00`, deixando a suíte determinística independente do ambiente.

4. O chat estava no frontend ativo, mas faltava API real compatível no backend.
   - Motivo: as rotas `/chat/reserva/:bookingId` e `/chat/viagem/:tripId` chamavam `GET/POST /api/bookings/<id>/messages/` e `GET/POST /api/trips/<id>/messages/`, mas o backend não expunha essas URLs.
   - Mudança: foram criados endpoints de listar/enviar mensagens para reserva e viagem.
   - Mudança: o model de mensagem ganhou vínculo opcional com `Booking` para separar conversa 1:1 de reserva do chat em grupo da viagem.
   - Mudança: as regras de permissão foram corrigidas para reconhecer motorista pelo `ProfileDriver.user_id` e passageiros confirmados pelo status da reserva.

## O que foi auditado mas não alterado

1. `frontend/src/agenda/*` chama `/api/bookings/my-trips/` e `PATCH /api/trips/<id>/cancel/`.
   - Decisão: não implementei agora porque essa agenda antiga não está ligada às rotas atuais do `App.tsx`.
   - Risco: se essa tela voltar a ser usada, esses endpoints precisarão ser implementados ou o frontend deverá migrar para os serviços atuais.

2. O backend expõe endpoints que ainda não têm tela ativa consumindo tudo.
   - Exemplos: custo direto da viagem, recálculo/reordenação de rota.
   - Decisão: não removi nem forcei tela nova, porque são APIs úteis para evolução e não quebram o fluxo atual.

3. Criação completa de viagem depende de Mapbox real.
   - Resultado do teste: com token placeholder, o backend retornou erro controlado e não persistiu viagem/custo parcial.
   - Para validar sucesso fim a fim, é necessário subir Docker com `MAPBOX_ACCESS_TOKEN` válido.

## Validações executadas

- `docker compose -f backend/infra/compose/docker-compose.dev.yaml config`
- `docker compose -f backend/infra/compose/docker-compose.dev.yaml up --build -d`
- `docker compose -f backend/infra/compose/docker-compose.dev.yaml exec -T backend python manage.py makemigrations --check --dry-run`
  - Resultado: `No changes detected`.
- `docker compose -f backend/infra/compose/docker-compose.dev.yaml exec -T backend python manage.py check`
  - Resultado: `System check identified no issues (0 silenced).`
- `docker compose -f backend/infra/compose/docker-compose.dev.yaml exec -T backend pytest -c /pytest.ini /app`
  - Resultado: `77 passed, 4 skipped`.
- `docker compose -f backend/infra/compose/docker-compose.dev.yaml exec -T frontend npm run build`
  - Resultado: build passou; permaneceu apenas o aviso conhecido de chunk acima de 500 kB.
- `docker compose -f backend/infra/compose/docker-compose.dev.yaml exec -T frontend npm run lint`
  - Resultado: lint passou.
- Smoke real de browser com `VITE_USE_MOCK=false`.
  - Login real via frontend com usuário passageiro criado no banco Docker.
  - `GET /api/bookings/1/messages/` carregou a mensagem existente no chat de reserva.
  - `POST /api/bookings/1/messages/` via UI criou `Mensagem pela UI reserva 1783552444885`.
  - `GET /api/trips/3/messages/` carregou a mensagem existente no chat de viagem.
  - `POST /api/trips/3/messages/` via UI criou `Mensagem pela UI viagem 1783552466096`.
  - Consulta direta no banco confirmou as duas mensagens persistidas com `booking_id=1` para reserva e `booking_id=null` para viagem.
