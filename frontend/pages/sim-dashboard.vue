<template>
  <section>
    <h1>Simulation dashboard</h1>
    <p class="subtitle">Monitor system health, demand, and simulated routes.</p>

    <div class="section grid">
      <div class="card stat">
        <span class="subtitle">Graph nodes</span>
        <span class="stat-value">{{ graph?.nodes?.length ?? 0 }}</span>
      </div>
      <div class="card stat">
        <span class="subtitle">Graph edges</span>
        <span class="stat-value">{{ graph?.edges?.length ?? 0 }}</span>
      </div>
      <div class="card stat">
        <span class="subtitle">Last refresh</span>
        <span class="stat-value">{{ timestamp }}</span>
      </div>
    </div>

    <div class="section card">
      <h2>Find path</h2>
      <form class="form" @submit.prevent="findPath">
        <div>
          <label for="start">Start stop</label>
          <input id="start" v-model="pathForm.start" type="text" placeholder="Origin" />
        </div>
        <div>
          <label for="end">End stop</label>
          <input id="end" v-model="pathForm.end" type="text" placeholder="Destination" />
        </div>
        <div class="form-actions">
          <button class="button" type="submit" :disabled="loading">
            {{ loading ? 'Calculating...' : 'Calculate path' }}
          </button>
        </div>
        <p v-if="errorMessage" class="alert">{{ errorMessage }}</p>
      </form>

      <div v-if="pathResult" class="section">
        <h3>Shortest path</h3>
        <p>Distance: {{ pathResult.distance ?? 'N/A' }}</p>
        <p>Path: {{ pathResult.path?.join(' → ') || 'No path found' }}</p>
      </div>
    </div>
  </section>
</template>

<script setup>
const config = useRuntimeConfig();
const apiBase = config.public.apiBase;

const timestamp = ref(new Date().toLocaleTimeString());

const { data: graphData, refresh: refreshGraph } = await useFetch(`${apiBase}/api/sim/graph`, {
  credentials: 'include',
});

const graph = computed(() => graphData.value);

const pathForm = reactive({
  start: '',
  end: '',
});

const loading = ref(false);
const errorMessage = ref('');
const pathResult = ref(null);

const findPath = async () => {
  errorMessage.value = '';
  pathResult.value = null;

  if (!pathForm.start || !pathForm.end) {
    errorMessage.value = 'Start and end stops are required.';
    return;
  }

  loading.value = true;
  try {
    const response = await $fetch(`${apiBase}/api/sim/path`, {
      method: 'POST',
      credentials: 'include',
      body: {
        start: pathForm.start,
        end: pathForm.end,
      },
    });

    pathResult.value = response;
    timestamp.value = new Date().toLocaleTimeString();
    await refreshGraph();
  } catch (error) {
    errorMessage.value = error?.data?.error || 'Unable to compute path.';
  } finally {
    loading.value = false;
  }
};
</script>
