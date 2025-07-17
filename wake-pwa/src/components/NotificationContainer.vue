<template>
  <teleport to="body">
    <div class="fixed top-4 right-4 z-50 space-y-3 w-full max-w-md pointer-events-none">
      <div class="space-y-3 pointer-events-auto">
      <transition-group
        name="notification"
        tag="div"
        class="space-y-3"
      >
        <div
          v-for="notification in notifications"
          :key="notification.id"
          :class="[
            'w-full min-w-[320px] max-w-md shadow-xl rounded-xl pointer-events-auto overflow-hidden border-l-4',
            notificationClasses(notification.type)
          ]"
        >
          <div class="p-5">
            <div class="flex items-start space-x-4">
              <div class="flex-shrink-0">
                <div class="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold text-lg">
                  {{ getIcon(notification.type) }}
                </div>
              </div>
              <div class="flex-1 min-w-0">
                <h4 class="text-base font-semibold text-white mb-1 break-words">
                  {{ notification.title }}
                </h4>
                <p v-if="notification.message" class="text-sm text-white/90 break-words leading-relaxed">
                  {{ notification.message }}
                </p>
              </div>
              <div class="flex-shrink-0">
                <button
                  @click="removeNotification(notification.id)"
                  class="text-white/80 hover:text-white text-xl font-bold w-6 h-6 flex items-center justify-center rounded-full hover:bg-white/20 transition-colors"
                  aria-label="Cerrar notificación"
                >
                  &times;
                </button>
              </div>
            </div>
          </div>
        </div>
      </transition-group>
      </div>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { useNotifications } from '@/composables/useNotifications'

const { notifications, removeNotification } = useNotifications()

const notificationClasses = (type: string) => {
  const classes = {
    success: 'bg-gradient-to-r from-green-500 to-green-600 border-l-green-400',
    error: 'bg-gradient-to-r from-red-500 to-red-600 border-l-red-400',
    warning: 'bg-gradient-to-r from-amber-500 to-orange-500 border-l-amber-400',
    info: 'bg-gradient-to-r from-blue-500 to-blue-600 border-l-blue-400'
  }
  return classes[type as keyof typeof classes] || classes.info
}

const getIcon = (type: string) => {
  const icons = {
    success: '✓',
    error: '✕',
    warning: '!',
    info: 'i'
  }
  return icons[type as keyof typeof icons] || icons.info
}
</script>

<style scoped>
.notification-enter-active {
  transition: all 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
}

.notification-leave-active {
  transition: all 0.3s ease-in;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.9);
}

.notification-move {
  transition: transform 0.3s ease;
}

/* Asegurar que las notificaciones sean responsivas */
@media (max-width: 640px) {
  .fixed.top-4.right-4 {
    top: 1rem;
    right: 1rem;
    left: 1rem;
    max-width: none;
  }
}
</style>