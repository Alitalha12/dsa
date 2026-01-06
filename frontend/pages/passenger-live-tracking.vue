<template>
  <section>
    <h1>Live tracking</h1>
    <p class="subtitle">Monitor active buses and their estimated arrivals.</p>

    <div class="section card">
      <div class="card-header">
        <h2>Active buses</h2>
        <button class="button ghost" type="button" @click="refresh">Refresh</button>
      </div>
      <div class="grid">
        <div v-for="bus in buses" :key="bus.bus_number" class="card">
          <h3>{{ bus.bus_number }}</h3>
          <p>Route: {{ bus.route_name }}</p>
          <p>Current stop: {{ bus.current_stop }}</p>
          <p>Next stop: {{ bus.next_stop }}</p>
          <p>ETA: {{ bus.eta }}</p>
        </div>
        <p v-if="!buses.length">No live buses available or login required.</p>
      </div>
    </div>
  </section>
</template>

<script setup>
const config = useRuntimeConfig();
const apiBase = config.public.apiBase;

const { data, refresh } = await useFetch(`${apiBase}/api/tracking/live_buses`, {
  credentials: 'include',
});

const buses = computed(() => data.value?.live_buses ?? []);
</script>
