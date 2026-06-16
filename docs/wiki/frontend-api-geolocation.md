# Comunicacao frontend e recursos do navegador

Responsavel: `jordancarvaalho`

## Tecnologia abordada

Este tutorial mostra como o frontend pode se comunicar com uma API usando Axios e como usar recursos do navegador para apoiar campos de origem e destino. Para evitar dependencia de chave externa, o exemplo usa autocomplete mockado e a Geolocation API de forma conceitual.

## Instalacao e configuracao minima

Requisitos:

- Frontend React/Vite configurado.
- Axios instalado no projeto.
- Navegador moderno para testar geolocalizacao.

Instalacao do Axios, se necessario:

```bash
cd frontend
npm install axios
```

## Exemplo funcional

O exemplo abaixo cria um cliente HTTP, uma busca mockada de enderecos e uma funcao para ler a localizacao atual do navegador.

```ts
import axios from 'axios'

export const api = axios.create({
  baseURL: 'http://localhost:8000/api',
})

const addresses = [
  'Teresina, PI',
  'Parnaiba, PI',
  'Picos, PI',
  'Floriano, PI',
]

export async function searchAddresses(term: string) {
  return addresses.filter((address) =>
    address.toLowerCase().includes(term.toLowerCase()),
  )
}

export function getCurrentPosition() {
  return new Promise<GeolocationPosition>((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error('Geolocalizacao nao suportada pelo navegador.'))
      return
    }

    navigator.geolocation.getCurrentPosition(resolve, reject)
  })
}
```

Exemplo de uso em componente:

```tsx
import { useState } from 'react'
import { getCurrentPosition, searchAddresses } from './locationService'

export function LocationExample() {
  const [term, setTerm] = useState('')
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [currentLocation, setCurrentLocation] = useState('')

  async function handleChange(value: string) {
    setTerm(value)
    setSuggestions(await searchAddresses(value))
  }

  async function handleUseCurrentLocation() {
    const position = await getCurrentPosition()

    setCurrentLocation(
      `${position.coords.latitude}, ${position.coords.longitude}`,
    )
  }

  return (
    <section>
      <label>
        Origem
        <input value={term} onChange={(event) => handleChange(event.target.value)} />
      </label>

      <button type="button" onClick={handleUseCurrentLocation}>
        Usar localizacao atual
      </button>

      <ul>
        {suggestions.map((suggestion) => (
          <li key={suggestion}>{suggestion}</li>
        ))}
      </ul>

      {currentLocation && <p>Localizacao atual: {currentLocation}</p>}
    </section>
  )
}
```

## O que demonstrar no video

- Mostrar a criacao de um service com Axios.
- Explicar a diferenca entre chamada real e mock local.
- Digitar em um campo e listar sugestoes mockadas.
- Clicar em "usar localizacao atual" e explicar a permissao do navegador.
- Reforcar que API real de mapas fica fora do tutorial minimo.

## Links oficiais

- Axios: https://axios-http.com/docs/intro
- MDN Geolocation API: https://developer.mozilla.org/en-US/docs/Web/API/Geolocation_API
- MDN Fetch API, como referencia alternativa: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API

