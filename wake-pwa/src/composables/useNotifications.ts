import { ref, reactive } from 'vue'

export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
  persistent?: boolean
}

const notifications = ref<Notification[]>([])

export const useNotifications = () => {
  const showNotification = (notification: Omit<Notification, 'id'>) => {
    const id = Date.now().toString()
    const newNotification: Notification = {
      id,
      duration: 5000,
      persistent: false,
      ...notification
    }

    notifications.value.push(newNotification)

    if (!newNotification.persistent) {
      setTimeout(() => {
        removeNotification(id)
      }, newNotification.duration)
    }

    return id
  }

  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clearAll = () => {
    notifications.value.splice(0)
  }

  const success = (title: string, message?: string, options?: Partial<Notification>) => {
    return showNotification({ 
      type: 'success', 
      title, 
      message, 
      duration: 4000,
      ...options 
    })
  }

  const error = (title: string, message?: string, options?: Partial<Notification>) => {
    return showNotification({ 
      type: 'error', 
      title, 
      message, 
      duration: 6000,
      ...options 
    })
  }

  const warning = (title: string, message?: string, options?: Partial<Notification>) => {
    return showNotification({ 
      type: 'warning', 
      title, 
      message, 
      duration: 5000,
      ...options 
    })
  }

  const info = (title: string, message?: string, options?: Partial<Notification>) => {
    return showNotification({ 
      type: 'info', 
      title, 
      message, 
      duration: 4000,
      ...options 
    })
  }

  return {
    notifications: notifications.value,
    showNotification,
    removeNotification,
    clearAll,
    success,
    error,
    warning,
    info
  }
}