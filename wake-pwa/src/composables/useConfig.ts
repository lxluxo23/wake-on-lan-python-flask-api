import { computed, readonly } from 'vue'

/**
 * Composable para manejo centralizado de configuración y variables de entorno
 */
export const useConfig = () => {
  // Configuración del API
  const apiConfig = computed(() => ({
    baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
    timeout: parseInt(import.meta.env.VITE_DEFAULT_TIMEOUT || '10000'),
    maxRetries: parseInt(import.meta.env.VITE_MAX_RETRIES || '3'),
  }))

  // Información de la aplicación
  const appInfo = computed(() => ({
    title: import.meta.env.VITE_APP_TITLE || 'Wake-on-LAN Remote',
    version: import.meta.env.VITE_APP_VERSION || '1.0.0',
    environment: import.meta.env.VITE_ENVIRONMENT || 'development',
  }))

  // Configuración del entorno
  const envConfig = computed(() => ({
    isDevelopment: import.meta.env.DEV,
    isProduction: import.meta.env.PROD,
    mode: import.meta.env.MODE,
    debug: import.meta.env.VITE_DEBUG === 'true',
  }))

  // URLs completas para diferentes endpoints
  const apiUrls = computed(() => {
    const baseURL = apiConfig.value.baseURL
    return {
      auth: {
        login: `${baseURL}/auth/login`,
        register: `${baseURL}/auth/register`,
        logout: `${baseURL}/auth/logout`,
      },
      equipos: {
        list: `${baseURL}/equipos`,
        create: `${baseURL}/equipos`,
        update: (id: number) => `${baseURL}/equipos/${id}`,
        delete: (id: number) => `${baseURL}/equipos/${id}`,
        wake: (id: number) => `${baseURL}/equipos/${id}/encender`,
        status: (id: number) => `${baseURL}/equipos/${id}/estado`,
      },
    }
  })

  // Función para logging en desarrollo
  const log = (...args: any[]) => {
    if (envConfig.value.debug && envConfig.value.isDevelopment) {
      console.log('[Wake-on-LAN]', ...args)
    }
  }

  // Función para errores
  const logError = (...args: any[]) => {
    if (envConfig.value.debug) {
      console.error('[Wake-on-LAN Error]', ...args)
    }
  }

  // Función para obtener toda la configuración como un objeto plano
  const getAllConfig = () => ({
    api: apiConfig.value,
    app: appInfo.value,
    env: envConfig.value,
    urls: apiUrls.value,
  })

  return {
    // Configuraciones readonly para evitar modificaciones accidentales
    apiConfig: readonly(apiConfig),
    appInfo: readonly(appInfo),
    envConfig: readonly(envConfig),
    apiUrls: readonly(apiUrls),
    
    // Utilidades
    log,
    logError,
    getAllConfig,
    
    // Acceso directo a valores comunes
    apiBaseURL: computed(() => apiConfig.value.baseURL),
    appTitle: computed(() => appInfo.value.title),
    isDebug: computed(() => envConfig.value.debug),
    isDev: computed(() => envConfig.value.isDevelopment),
    isProd: computed(() => envConfig.value.isProduction),
  }
}