<template>
  <section>
    <h1>Book ticket</h1>
    <p class="subtitle">Reserve a seat on your preferred route.</p>

    <div class="card" style="max-width: 720px;">
      <form class="form" @submit.prevent="searchBuses">
        <div>
          <label for="from">From stop</label>
          <input id="from" v-model="form.from_stop" type="text" placeholder="Start stop" />
        </div>
        <div>
          <label for="to">To stop</label>
          <input id="to" v-model="form.to_stop" type="text" placeholder="Destination stop" />
        </div>
        <div>
          <label for="date">Travel date</label>
          <input id="date" v-model="form.date" type="date" />
        </div>
        <div class="form-actions">
          <button class="button" type="submit" :disabled="loading">
            {{ loading ? 'Searching...' : 'Search buses' }}
          </button>
          <NuxtLink class="button secondary" to="/passenger-dashboard">Back</NuxtLink>
        </div>
        <p v-if="errorMessage" class="alert">{{ errorMessage }}</p>
      </form>
    </div>

    <div class="section card" v-if="availableBuses.length">
      <h2>Available buses</h2>
      <table class="table">
        <thead>
          <tr>
            <th>Bus</th>
            <th>Route</th>
            <th>Departure</th>
            <th>Arrival</th>
            <th>Fare</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="bus in availableBuses" :key="bus.bus_number">
            <td>{{ bus.bus_number }}</td>
            <td>{{ bus.route_name }}</td>
            <td>{{ bus.departure_time }}</td>
            <td>{{ bus.arrival_time }}</td>
            <td>{{ bus.fare }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
const config = useRuntimeConfig();
const apiBase = config.public.apiBase;

const form = reactive({
  from_stop: '',
  to_stop: '',
  date: '',
});

const loading = ref(false);
const errorMessage = ref('');
const availableBuses = ref([]);

const searchBuses = async () => {
  errorMessage.value = '';
  availableBuses.value = [];

  if (!form.from_stop || !form.to_stop || !form.date) {
    errorMessage.value = 'Please provide origin, destination, and date.';
    return;
  }

  loading.value = true;
  try {
    const response = await $fetch(`${apiBase}/api/book/available_buses`, {
      method: 'POST',
      credentials: 'include',
      body: {
        from_stop: form.from_stop,
        to_stop: form.to_stop,
        date: form.date,
      },
    });
    availableBuses.value = response?.buses ?? [];
  } catch (error) {
    errorMessage.value = error?.data?.error || 'Unable to fetch buses.';
  } finally {
    loading.value = false;
  }
};
</script>
