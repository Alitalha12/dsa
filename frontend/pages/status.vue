<template>
  <section>
    <h1>API status</h1>
    <p class="subtitle">Live health information from the Python backend.</p>

    <div class="section grid">
      <div class="card">
        <h3>Health</h3>
        <p v-if="pending">Checking backend health...</p>
        <p v-else-if="error" class="alert">Unable to reach the backend.</p>
        <p v-else>✅ {{ data.status }} ({{ data.timestamp }})</p>
      </div>
      <div class="card">
        <h3>Routes</h3>
        <p v-if="routesPending">Loading...</p>
        <p v-else-if="routesError">Login required</p>
        <p v-else>Total routes: {{ routesData?.total ?? 0 }}</p>
      </div>
    </div>
  </section>
</template>

<script setup>
const config = useRuntimeConfig();
const apiBase = config.public.apiBase;

const { data, pending, error } = await useFetch(`${apiBase}/health`, {
  credentials: 'include',
});

const { data: routesData, pending: routesPending, error: routesError } = await useFetch(
  `${apiBase}/api/routes`,
  {
    credentials: 'include',
  },
);
</script>
