<template>
  <section>
    <h1>Bus management</h1>
    <p class="subtitle">Allocate buses, update statuses, and monitor capacity.</p>

    <div class="section card">
      <h2>Add new bus</h2>
      <form class="form" @submit.prevent="addBus">
        <div>
          <label for="bus-number">Bus number</label>
          <input id="bus-number" v-model="form.bus_number" type="text" placeholder="BUS-101" />
        </div>
        <div>
          <label for="plate-number">Plate number</label>
          <input id="plate-number" v-model="form.plate_number" type="text" placeholder="ABC-1234" />
        </div>
        <div>
          <label for="driver-name">Driver name</label>
          <input id="driver-name" v-model="form.driver_name" type="text" placeholder="Driver name" />
        </div>
        <div>
          <label for="capacity">Capacity</label>
          <input id="capacity" v-model.number="form.capacity" type="number" min="1" placeholder="50" />
        </div>
        <div class="form-actions">
          <button class="button" type="submit" :disabled="saving">
            {{ saving ? 'Saving...' : 'Add bus' }}
          </button>
          <button class="button secondary" type="button" @click="resetForm">Clear</button>
        </div>
        <p v-if="saveError" class="alert">{{ saveError }}</p>
      </form>
    </div>

    <div class="section grid">
      <div class="card stat">
        <span class="subtitle">Active buses</span>
        <span class="stat-value">{{ stats?.active_buses ?? 0 }}</span>
      </div>
      <div class="card stat">
        <span class="subtitle">Maintenance</span>
        <span class="stat-value">{{ stats?.maintenance_buses ?? 0 }}</span>
      </div>
      <div class="card stat">
        <span class="subtitle">Inactive</span>
        <span class="stat-value">{{ stats?.inactive_buses ?? 0 }}</span>
      </div>
    </div>

    <div class="section card">
      <div class="card-header">
        <h2>Fleet overview</h2>
        <button class="button ghost" type="button" @click="refreshBuses">Refresh</button>
      </div>
      <table class="table">
        <thead>
          <tr>
            <th>Bus</th>
            <th>Route</th>
            <th>Status</th>
            <th>Capacity</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="bus in buses" :key="bus.id">
            <td>{{ bus.bus_number }}</td>
            <td>{{ bus.route_name || 'Unassigned' }}</td>
            <td>
              <span class="badge" :class="statusClass(bus.status)">{{ bus.status }}</span>
            </td>
            <td>{{ bus.current_passengers ?? 0 }} / {{ bus.capacity }}</td>
          </tr>
          <tr v-if="!buses.length">
            <td colspan="4">No buses available or login required.</td>
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
  bus_number: '',
  plate_number: '',
  driver_name: '',
  capacity: 50,
});

const saving = ref(false);
const saveError = ref('');

const {
  data: busesData,
  refresh: refreshBuses,
} = await useFetch(`${apiBase}/admin/api/buses`, {
  credentials: 'include',
});

const { data: stats } = await useFetch(`${apiBase}/admin/api/buses/statistics`, {
  credentials: 'include',
});

const buses = computed(() => busesData.value?.buses ?? []);

const resetForm = () => {
  form.bus_number = '';
  form.plate_number = '';
  form.driver_name = '';
  form.capacity = 50;
};

const addBus = async () => {
  saveError.value = '';
  if (!form.bus_number || !form.plate_number || !form.driver_name) {
    saveError.value = 'Bus number, plate number, and driver name are required.';
    return;
  }

  saving.value = true;
  try {
    await $fetch(`${apiBase}/admin/api/buses`, {
      method: 'POST',
      credentials: 'include',
      body: {
        ...form,
      },
    });
    resetForm();
    await refreshBuses();
  } catch (error) {
    saveError.value = error?.data?.error || 'Unable to add bus.';
  } finally {
    saving.value = false;
  }
};

const statusClass = (status) => {
  if (status === 'active') return 'success';
  if (status === 'maintenance') return 'warning';
  return '';
};
</script>
