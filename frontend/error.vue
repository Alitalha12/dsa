<template>
  <section class="container page">
    <h1>{{ error?.statusCode || 500 }} - {{ error?.statusMessage || 'Unexpected error' }}</h1>
    <p class="subtitle">{{ error?.message || 'Please try again later.' }}</p>
    <NuxtLink class="button" to="/">Return home</NuxtLink>
  </section>
</template>

<script setup>
defineProps({
  error: {
    type: Object,
    required: true,
  },
});
</script>
