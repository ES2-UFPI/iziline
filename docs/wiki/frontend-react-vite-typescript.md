# Frontend com React, Vite e TypeScript

Responsavel: `micaiasdev`

## Tecnologia abordada

Este tutorial apresenta a base do frontend do Iziline usando React, Vite e TypeScript. O foco e criar componentes, controlar estado e rodar a aplicacao localmente.

## Instalacao e configuracao minima

Requisitos:

- Node.js instalado.
- npm instalado.
- Editor de codigo com suporte a TypeScript.

Comandos principais:

```bash
cd frontend
npm install
npm run dev
```

Validacao antes de entregar:

```bash
npm run build
npm run lint
```

## Exemplo funcional

O exemplo abaixo cria uma lista simples de viagens cadastradas em memoria.

```tsx
import { FormEvent, useState } from 'react'

type Trip = {
  origin: string
  destination: string
  date: string
}

export function TripExample() {
  const [origin, setOrigin] = useState('')
  const [destination, setDestination] = useState('')
  const [date, setDate] = useState('')
  const [trips, setTrips] = useState<Trip[]>([])

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    setTrips((currentTrips) => [
      ...currentTrips,
      { origin, destination, date },
    ])

    setOrigin('')
    setDestination('')
    setDate('')
  }

  return (
    <section>
      <h1>Nova viagem</h1>

      <form onSubmit={handleSubmit}>
        <input
          value={origin}
          onChange={(event) => setOrigin(event.target.value)}
          placeholder="Origem"
          required
        />

        <input
          value={destination}
          onChange={(event) => setDestination(event.target.value)}
          placeholder="Destino"
          required
        />

        <input
          type="date"
          value={date}
          onChange={(event) => setDate(event.target.value)}
          required
        />

        <button type="submit">Cadastrar</button>
      </form>

      <ul>
        {trips.map((trip) => (
          <li key={`${trip.origin}-${trip.destination}-${trip.date}`}>
            {trip.origin} para {trip.destination} em {trip.date}
          </li>
        ))}
      </ul>
    </section>
  )
}
```

## O que demonstrar no video

- Abrir a pasta `frontend`.
- Explicar rapidamente o papel de `src/main.tsx`, `src/App.tsx` e componentes.
- Criar ou explicar um componente React com TypeScript.
- Mostrar `useState` controlando o formulario.
- Executar `npm run dev` e cadastrar uma viagem no navegador.

## Links oficiais

- React Learn: https://react.dev/learn
- Vite Guide: https://vite.dev/guide/
- TypeScript com React: https://react.dev/learn/typescript

