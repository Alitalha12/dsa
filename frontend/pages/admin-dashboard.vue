<template>
  <section>
    <h1>Admin dashboard</h1>
    <p class="subtitle">Operational snapshot across routes, buses, and passengers.</p>

    <div class="section grid">
      <div class="card stat">
        <span class="subtitle">Total passengers</span>
        <span class="stat-value">
          <span v-if="dashboardPending">--</span>
          <span v-else-if="dashboardError">Login required</span>
          <span v-else>{{ dashboard?.total_passengers ?? 0 }}</span>
        </span>
      </div>
      <div class="card stat">
        <span class="subtitle">Active sessions</span>
        <span class="stat-value">
          <span v-if="dashboardPending">--</span>
          <span v-else-if="dashboardError">Login required</span>
          <span v-else>{{ dashboard?.active_sessions ?? 0 }}</span>
        </span>
      </div>
      <div class="card stat">
        <span class="subtitle">Total routes</span>
        <span class="stat-value">
          <span v-if="routesPending">--</span>
          <span v-else-if="routesError">Login required</span>
          <span v-else>{{ routesStats?.stats?.total_routes ?? 0 }}</span>
        </span>
      </div>
      <div class="card stat">
        <span class="subtitle">Fleet size</span>
        <span class="stat-value">
          <span v-if="busPending">--</span>
          <span v-else-if="busError">Login required</span>
          <span v-else>{{ busStats?.total_buses ?? 0 }}</span>
        </span>
      </div>
    </div>

    <div class="section grid">
      <div class="card">
        <div class="card-header">
          <h3>Bus health</h3>
          <NuxtLink to="/admin-bus-management">Manage buses</NuxtLink>
        </div>
        <p>Active: {{ busStats?.active_buses ?? 0 }}</p>
        <p>Maintenance: {{ busStats?.maintenance_buses ?? 0 }}</p>
        <p>Inactive: {{ busStats?.inactive_buses ?? 0 }}</p>
      </div>
      <div class="card">
        <div class="card-header">
          <h3>Route activity</h3>
          <NuxtLink to="/admin-routes">Manage routes</NuxtLink>
        </div>
        <p>Total stops: {{ routesStats?.stats?.total_stops ?? 0 }}</p>
        <p>Average stops per route: {{ routesStats?.stats?.avg_stops_per_route ?? 0 }}</p>
      </div>
      <div class="card">
        <div class="card-header">
          <h3>System status</h3>
        </div>
        <p v-if="dashboardPending">Loading...</p>
        <p v-else-if="dashboardError">Login required</p>
        <p v-else>{{ dashboard?.system_status }} — {{ dashboard?.last_updated }}</p>
      </div>
    </div>
  </section>
</template>

<script setup>
const config = useRuntimeConfig();
const apiBase = config.public.apiBase;

const { data: dashboard, pending: dashboardPending, error: dashboardError } = await useFetch(
  `${apiBase}/admin/dashboard_stats`,
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
