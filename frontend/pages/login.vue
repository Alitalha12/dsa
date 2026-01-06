<template>
  <section>
    <h1>Sign in</h1>
    <p class="subtitle">Authenticate to access admin or passenger features.</p>

    <div class="card" style="max-width: 520px;">
      <form class="form" @submit.prevent="submitLogin">
        <div>
          <label for="username">Username</label>
          <input id="username" v-model="form.username" type="text" placeholder="Enter username" />
        </div>
        <div>
          <label for="password">Password</label>
          <input id="password" v-model="form.password" type="password" placeholder="Enter password" />
        </div>
        <div>
          <label>
            <input v-model="form.remember" type="checkbox" /> Remember me
          </label>
        </div>
        <div class="form-actions">
          <button class="button" type="submit" :disabled="loading">
            {{ loading ? 'Signing in...' : 'Sign in' }}
          </button>
          <NuxtLink class="button secondary" to="/signup">Create account</NuxtLink>
        </div>
        <p v-if="errorMessage" class="alert">{{ errorMessage }}</p>
        <p v-if="successMessage" class="notice">{{ successMessage }}</p>
      </form>
    </div>
  </section>
</template>

<script setup>
const config = useRuntimeConfig();
const apiBase = config.public.apiBase;

const form = reactive({
  username: '',
  password: '',
  remember: false,
});

const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

const submitLogin = async () => {
  errorMessage.value = '';
  successMessage.value = '';

  if (!form.username || !form.password) {
    errorMessage.value = 'Username and password are required.';
    return;
  }

  loading.value = true;
  try {
    const body = new URLSearchParams({
      username: form.username,
      password: form.password,
      remember: form.remember ? 'on' : '',
    });

    const response = await fetch(`${apiBase}/login`, {
      method: 'POST',
      body,
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Invalid credentials');
    }

    const redirectedUrl = response.url || '';
    successMessage.value = 'Login successful. Redirecting...';

    if (redirectedUrl.includes('/admin')) {
      await navigateTo('/admin-dashboard');
    } else {
      await navigateTo('/passenger-dashboard');
    }
  } catch (error) {
    errorMessage.value = 'Unable to sign in. Please check your credentials.';
  } finally {
    loading.value = false;
  }
};
</script>
