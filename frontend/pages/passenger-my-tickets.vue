<template>
  <section>
    <h1>My tickets</h1>
    <p class="subtitle">Review confirmed and past bookings.</p>

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

    <div class="section card">
      <h2>Tickets</h2>
      <p class="subtitle">
        Ticket listing will be exposed via a dedicated endpoint once the backend
        provides it. Use the legacy Flask view for now.
      </p>
      <a class="button" :href="`${apiBase}/passenger/my_tickets`" target="_blank" rel="noreferrer">
        Open legacy tickets view
      </a>
    </div>
  </section>
</template>

<script setup>
const config = useRuntimeConfig();
const apiBase = config.public.apiBase;

const { data: stats } = await useFetch(`${apiBase}/api/passenger/stats`, {
  credentials: 'include',
});
</script>
