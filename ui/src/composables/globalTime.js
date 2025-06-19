import { ref } from 'vue'

export const globalTime = ref({
  start: '2025-03-02T00:00:00',
  end: '2025-03-02T23:59:59Z'
})

export function useGlobalTime() {
  // Function to update the global time range
  const updateTimeRange = (startDateTime, endDateTime) => {
    globalTime.value = {
      start: startDateTime,
      end: endDateTime || `${startDateTime.split('T')[0]}T23:59:59Z`
    }
  }

  return {
    globalTime,
    updateTimeRange
  }
}
