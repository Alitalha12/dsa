<template>
  <section>
    <h1>Passenger dashboard</h1>
    <p class="subtitle">Manage tickets, plan journeys, and track buses.</p>

    <div class="section grid">
      <div class="card stat">
        <span class="subtitle">Total tickets</span>
        <span class="stat-value">{{ stats?.stats?.total_tickets ?? 0 }}</span>
      </div>
      <div class="card stat">
        <span class="subtitle">Active tickets</span>
        <span class="stat-value">{{ stats?.stats?.active_tickets ?? 0 }}</span>
      </div>
      <div class="card stat">
        <span class="subtitle">Total spent</span>
        <span class="stat-value">{{ stats?.stats?.total_spent ?? 0 }}</span>
      </div>
    </div>

    <div class="section grid">
      <div class="card">
        <h3>Book a ticket</h3>
        <p>Reserve a seat and manage upcoming travel.</p>
        <NuxtLink to="/passenger-book-ticket">Start booking →</NuxtLink>
      </div>
      <div class="card">
        <h3>Plan journey</h3>
        <p>Find the shortest route between stops.</p>
        <NuxtLink to="/passenger-plan-journey">Plan route →</NuxtLink>
      </div>
      <div class="card">
        <h3>Live tracking</h3>
        <p>Monitor buses in transit.</p>
        <NuxtLink to="/passenger-live-tracking">Track buses →</NuxtLink>
      </div>
      <div class="card">
        <h3>My tickets</h3>
        <p>Review and download previous tickets.</p>
        <NuxtLink to="/passenger-my-tickets">View tickets →</NuxtLink>
      </div>
    </div>

    <div class="section card">
      <div class="card-header">
        <h2>Live buses</h2>
        <button class="button ghost" type="button" @click="refreshLiveBuses">Refresh</button>
      </div>
      <div class="grid">
        <div v-for="bus in liveBuses" :key="bus.bus_number" class="card">
          <h3>{{ bus.bus_number }}</h3>
          <p>Route: {{ bus.route_name }}</p>
          <p>Current stop: {{ bus.current_stop }}</p>
          <p>ETA: {{ bus.eta }}</p>
        </div>
        <p v-if="!liveBuses.length">No live buses available or login required.</p>
      </div>
    </div>
  </section>
</template>

<script setup>
const config = useRuntimeConfig();
const apiBase = config.public.apiBase;

const { data: stats } = await useFetch(`${apiBase}/api/passenger/stats`, {
  credentials: 'include',
});

const { data: liveBusData, refresh: refreshLiveBuses } = await useFetch(
  `${apiBase}/api/tracking/live_buses`,
  {
    credentials: 'include',
  },
);

const liveBuses = computed(() => liveBusData.value?.live_buses ?? []);
</script>
