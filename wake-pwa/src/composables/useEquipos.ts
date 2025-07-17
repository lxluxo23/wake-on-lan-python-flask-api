import { ref, computed } from 'vue'
import { useApi } from './useApi'
import type { Equipo, CreateEquipoData, UpdateEquipoData, ApiResponse } from '@/types'

export function useEquipos() {
  const { get, post, put, delete: del, loading } = useApi()
  const equipos = ref<Equipo[]>([])
  const currentEquipo = ref<Equipo | null>(null)

  async function fetchEquipos(): Promise<void> {
    try {
      const response: ApiResponse = await get('/equipos')
      if (response.success && response.equipos) {
        equipos.value = response.equipos
      }
    } catch (error) {
      throw error
    }
  }

  async function fetchEquipo(id: number): Promise<Equipo | null> {
    try {
      const response: ApiResponse = await get(`/equipos/${id}`)
      if (response.success && response.equipo) {
        currentEquipo.value = response.equipo
        return response.equipo
      }
      return null
    } catch (error) {
      throw error
    }
  }

  async function createEquipo(equipoData: CreateEquipoData): Promise<boolean> {
    try {
      const response: ApiResponse = await post('/equipos', equipoData)
      if (response.success) {
        await fetchEquipos() // Recargar lista
        return true
      }
      return false
    } catch (error) {
      throw error
    }
  }

  async function updateEquipo(id: number, equipoData: UpdateEquipoData): Promise<boolean> {
    try {
      const response: ApiResponse = await put(`/equipos/${id}`, equipoData)
      if (response.success) {
        await fetchEquipos() // Recargar lista
        return true
      }
      return false
    } catch (error) {
      throw error
    }
  }

  async function deleteEquipo(id: number): Promise<boolean> {
    try {
      const response: ApiResponse = await del(`/equipos/${id}`)
      if (response.success) {
        equipos.value = equipos.value.filter(eq => eq.id !== id)
        return true
      }
      return false
    } catch (error) {
      throw error
    }
  }

  async function wakeEquipo(id: number): Promise<boolean> {
    try {
      const response: ApiResponse = await post(`/equipos/${id}/encender`)
      return response.success || false
    } catch (error) {
      throw error
    }
  }

  async function getEquipoStatus(id: number): Promise<Equipo | null> {
    try {
      const response: ApiResponse = await get(`/equipos/${id}/estado`)
      if (response.success && response.equipo) {
        // Actualizar el equipo en la lista
        const index = equipos.value.findIndex(eq => eq.id === id)
        if (index !== -1) {
          equipos.value[index] = response.equipo
        }
        return response.equipo
      }
      return null
    } catch (error) {
      throw error
    }
  }

  // Función para formatear MAC address
  function formatMacAddress(value: string): string {
    const cleaned = value.replace(/[^a-fA-F0-9]/g, '').toUpperCase()
    const formatted = cleaned.match(/.{1,2}/g)?.join(':') || cleaned
    return formatted.slice(0, 17)
  }

  // Función para validar MAC address
  function validateMacAddress(mac: string): boolean {
    const macRegex = /^([0-9A-F]{2}:){5}[0-9A-F]{2}$/
    return macRegex.test(mac)
  }

  return {
    equipos: computed(() => equipos.value),
    currentEquipo: computed(() => currentEquipo.value),
    loading,
    fetchEquipos,
    fetchEquipo,
    createEquipo,
    updateEquipo,
    deleteEquipo,
    wakeEquipo,
    getEquipoStatus,
    formatMacAddress,
    validateMacAddress
  }
}