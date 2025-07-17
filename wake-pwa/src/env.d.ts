/// <reference types="vite/client" />

declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

interface ImportMetaEnv {
  // URLs y configuración del API
  readonly VITE_API_URL: string
  
  // Información de la aplicación
  readonly VITE_APP_TITLE: string
  readonly VITE_APP_VERSION: string
  
  // Configuración del entorno
  readonly VITE_ENVIRONMENT: 'development' | 'production' | 'staging'
  readonly VITE_DEBUG: string
  
  // Configuración de la aplicación
  readonly VITE_DEFAULT_TIMEOUT: string
  readonly VITE_MAX_RETRIES: string
  
  // Variables del entorno estándar
  readonly MODE: string
  readonly BASE_URL: string
  readonly PROD: boolean
  readonly DEV: boolean
  readonly SSR: boolean
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}