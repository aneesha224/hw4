import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './styles.css'
import './dynamic.css'
import './usability.css'
import './design.css'
import './auth.css'
import './cart.css'
import './chat.css'
import App from './App'

createRoot(document.getElementById('root')!).render(<StrictMode><App /></StrictMode>)
