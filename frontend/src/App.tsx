import { useEffect, useState } from 'react'
import './App.css'
import { RideSearchPage } from './carona/pages/RideSearchPage/RideSearchPage'
import { NewTripPage } from './travel/pages/NewTripPage/NewTripPage'
import { useAuth } from './auth/AuthContext'
import { LoginPage } from './auth/pages/LoginPage/LoginPage'

type AppView = 'newTrip' | 'rides'

function getViewFromPath(): AppView {
  return window.location.pathname === '/caronas' ? 'rides' : 'newTrip'
}

function App() {
  const [view, setView] = useState<AppView>(() => getViewFromPath())

  useEffect(() => {
    function handlePopState() {
      setView(getViewFromPath())
    }

    window.addEventListener('popstate', handlePopState)

    return () => {
      window.removeEventListener('popstate', handlePopState)
    }
  }, [])

  const { user, loading, logout } = useAuth()

  if (loading) {
    return <div style={{ padding: 32 }}>Carregando...</div>
  }

  if (!user) {
    return <LoginPage />
  }

  function navigateTo(path: string, nextView: AppView) {
    window.history.pushState({}, '', path)
    setView(nextView)
  }

  return (
    <>
      <nav className="app-navigation" aria-label="Navegação principal">
        <button
          type="button"
          className={view === 'newTrip' ? 'app-navigation__item active' : 'app-navigation__item'}
          onClick={() => navigateTo('/', 'newTrip')}
        >
          Cadastrar viagem
        </button>
        <button
          type="button"
          className={view === 'rides' ? 'app-navigation__item active' : 'app-navigation__item'}
          onClick={() => navigateTo('/caronas', 'rides')}
        >
          Buscar caronas
        </button>
        <button
          type="button"
          className="app-navigation__item"
          onClick={() => { void logout() }}
          style={{ marginLeft: 'auto' }}
        >
          Sair ({user.name})
        </button>
      </nav>

      {view === 'rides' ? <RideSearchPage /> : <NewTripPage />}
    </>
  )
}

export default App
