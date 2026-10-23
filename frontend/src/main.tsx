import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import { keycloak } from './auth'
import './styles.css'

const root = createRoot(document.getElementById('root')!)

keycloak
  .init({ onLoad: 'login-required', pkceMethod: 'S256', checkLoginIframe: false })
  .then(() => {
    root.render(
      <StrictMode>
        <App />
      </StrictMode>,
    )
  })
  .catch(() => root.render(<main className="login-error">Unable to start the local login flow.</main>))
