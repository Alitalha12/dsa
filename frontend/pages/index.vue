<template>
  <section>
    <span class="badge">Nuxt + Python stack</span>
    <h1>System overview</h1>
    <p class="subtitle">
      Live operational metrics pulled from the Python backend. Use the dashboard
      navigation to manage routes, buses, passengers, and simulations.
    </p>

    <div class="section grid">
      <div class="card stat">
        <span class="subtitle">System health</span>
        <span class="stat-value">
          <span v-if="healthPending">Loading...</span>
          <span v-else-if="healthError" class="alert">Unavailable</span>
          <span v-else>{{ health?.status }}</span>
        </span>
        <small class="subtitle">{{ health?.timestamp || 'No response yet' }}</small>
      </div>
      <div class="card stat">
        <span class="subtitle">Total routes</span>
        <span class="stat-value">
          <span v-if="routesPending">--</span>
          <span v-else-if="routesError">Login required</span>
          <span v-else>{{ routesStats?.stats?.total_routes ?? routesStats?.total_routes ?? 0 }}</span>
        </span>
      </div>
      <div class="card stat">
        <span class="subtitle">Total buses</span>
        <span class="stat-value">
          <span v-if="busPending">--</span>
          <span v-else-if="busError">Login required</span>
          <span v-else>{{ busStats?.total_buses ?? 0 }}</span>
        </span>
      </div>
    </div>

    <div class="section grid">
      <article class="card">
        <div class="card-header">
          <h3>Admin tools</h3>
          <NuxtLink to="/admin-dashboard">Open</NuxtLink>
        </div>
        <p>Manage buses, routes, and analytics from a single console.</p>
      </article>
      <article class="card">
        <div class="card-header">
          <h3>Passenger services</h3>
          <NuxtLink to="/passenger-dashboard">Open</NuxtLink>
        </div>
        <p>Booking, ticket tracking, and journey planning in one place.</p>
      </article>
      <article class="card">
        <div class="card-header">
          <h3>Simulation</h3>
          <NuxtLink to="/sim-dashboard">Open</NuxtLink>
        </div>
        <p>Visualize the routing graph and simulation outputs.</p>
      </article>
    </div>
  </section>
</template>

<script setup>
const config = useRuntimeConfig();
const apiBase = config.public.apiBase;

const { data: health, pending: healthPending, error: healthError } = await useFetch(
  `${apiBase}/health`,
  {
    credentials: 'include',
  },
);

const { data: routesStats, pending: routesPending, error: routesError } = await useFetch(
  `${apiBase}/api/routes/stats`,
  {
    credentials: 'include',
  },
);

const { data: busStats, pending: busPending, error: busError } = await useFetch(
  `${apiBase}/admin/api/buses/statistics`,
  {
    credentials: 'include',
  },
);
</script>
