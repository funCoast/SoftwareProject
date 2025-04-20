import { ref, watch } from 'vue'

export function usePersistentRef<T>(key: string, defaultValue: T) {
    const saved = localStorage.getItem(key)
    const state = ref<T>(saved ? JSON.parse(saved) : defaultValue)

    watch(state, (val) => {
        localStorage.setItem(key, JSON.stringify(val))
    }, { deep: true })

    return state
}