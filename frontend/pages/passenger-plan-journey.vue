<template>
  <section>
    <h1>Plan journey</h1>
    <p class="subtitle">Find the optimal path using the shortest-route engine.</p>

    <div class="card" style="max-width: 720px;">
      <form class="form" @submit.prevent="calculateRoute">
        <div>
          <label for="from-stop">From stop</label>
          <input id="from-stop" v-model="form.from_stop" type="text" placeholder="Origin" />
        </div>
        <div>
          <label for="to-stop">To stop</label>
          <input id="to-stop" v-model="form.to_stop" type="text" placeholder="Destination" />
        </div>
        <div>
          <label for="criteria">Criteria</label>
          <select id="criteria" v-model="form.criteria">
            <option value="time">Shortest time</option>
            <option value="distance">Shortest distance</option>
          </select>
        </div>
        <div class="form-actions">
          <button class="button" type="submit" :disabled="loading">
            {{ loading ? 'Calculating...' : 'Calculate route' }}
          </button>
          <NuxtLink class="button secondary" to="/passenger-dashboard">Back</NuxtLink>
        </div>
        <p v-if="errorMessage" class="alert">{{ errorMessage }}</p>
      </form>
    </div>

    <div class="section card" v-if="result">
      <h2>Suggested route</h2>
      <p>Distance: {{ result.distance ?? 'N/A' }}</p>
      <p>Path: {{ result.path?.join(' → ') || 'No path found' }}</p>
    </div>
  </section>
</template>

<script setup>
const config = useRuntimeConfig();
const apiBase = config.public.apiBase;

const form = reactive({
  from_stop: '',
  to_stop: '',
  criteria: 'time',
});

const result = ref(null);
const loading = ref(false);
const errorMessage = ref('');

const calculateRoute = async () => {
  errorMessage.value = '';
  result.value = null;

  if (!form.from_stop || !form.to_stop) {
    errorMessage.value = 'Please provide both stops.';
    return;
  }

  loading.value = true;
  try {
    const response = await $fetch(`${apiBase}/api/plan/shortest_route`, {
      method: 'POST',
      credentials: 'include',
      body: {
        from_stop: form.from_stop,
        to_stop: form.to_stop,
        criteria: form.criteria,
      },
    });
    result.value = response?.result || null;
  } catch (error) {
    errorMessage.value = error?.data?.error || 'Unable to calculate route.';
  } finally {
    loading.value = false;
  }
};
</script>
