<template>
  <section>
    <h1>Route management</h1>
    <p class="subtitle">Create, edit, and review route structures from the backend.</p>

    <div class="section card">
      <h2>Create new route</h2>
      <form class="form" @submit.prevent="createRoute">
        <div>
          <label for="route-name">Route name</label>
          <input id="route-name" v-model="routeName" type="text" placeholder="City Loop" />
        </div>
        <div class="form-actions">
          <button class="button" type="submit" :disabled="creating">
            {{ creating ? 'Creating...' : 'Save route' }}
          </button>
          <button class="button secondary" type="button" @click="routeName = ''">Reset</button>
        </div>
        <p v-if="createError" class="alert">{{ createError }}</p>
      </form>
    </div>

    <div class="section card">
      <div class="card-header">
        <h2>Existing routes</h2>
        <button class="button ghost" type="button" @click="refreshRoutes">Refresh</button>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th>Route</th>
            <th>Stops</th>
            <th>Updated</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="route in routes" :key="route.route_id">
            <td>{{ route.route_name }}</td>
            <td>{{ route.total_stops ?? route.stops?.length ?? 0 }}</td>
            <td>{{ route.last_updated || 'N/A' }}</td>
          </tr>
          <tr v-if="!routes.length">
            <td colspan="3">No routes available or login required.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </section>
</template>

<script setup>
const config = useRuntimeConfig();
const apiBase = config.public.apiBase;

const routeName = ref('');
const creating = ref(false);
const createError = ref('');

const {
  data: routesData,
  refresh: refreshRoutes,
} = await useFetch(`${apiBase}/api/routes`, {
  credentials: 'include',
});

const routes = computed(() => routesData.value?.routes ?? []);

const createRoute = async () => {
  createError.value = '';
  if (!routeName.value.trim()) {
    createError.value = 'Route name is required.';
    return;
  }

  creating.value = true;
  try {
    await $fetch(`${apiBase}/api/routes/create`, {
      method: 'POST',
      credentials: 'include',
      body: {
        route_name: routeName.value.trim(),
      },
    });
    routeName.value = '';
    await refreshRoutes();
  } catch (error) {
    createError.value = error?.data?.error || 'Unable to create route.';
  } finally {
    creating.value = false;
  }
};
</script>
