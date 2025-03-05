import { create } from 'zustand'

interface MetricsState {
  maxDevs: number
  hourlyRate: number
  weeksPerYear: number
  hoursPerWeek: number
  setMaxDevs: (value: number) => void
  setHourlyRate: (value: number) => void
  setWeeksPerYear: (value: number) => void
  setHoursPerWeek: (value: number) => void
}

export const useMetricsStore = create<MetricsState>((set) => ({
  maxDevs: 200,
  hourlyRate: 50,
  weeksPerYear: 48,
  hoursPerWeek: 3.5,
  setMaxDevs: (value: number) => set({ maxDevs: value }),
  setHourlyRate: (value: number) => set({ hourlyRate: value }),
  setWeeksPerYear: (value: number) => set({ weeksPerYear: value }),
  setHoursPerWeek: (value: number) => set({ hoursPerWeek: value }),
})) 