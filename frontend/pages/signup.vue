<template>
  <section>
    <h1>Create account</h1>
    <p class="subtitle">Register a passenger profile to access booking features.</p>

    <div class="card" style="max-width: 620px;">
      <form class="form" @submit.prevent="submitSignup">
        <div>
          <label for="full-name">Full name</label>
          <input id="full-name" v-model="form.full_name" type="text" placeholder="Enter your name" />
        </div>
        <div>
          <label for="username">Username</label>
          <input id="username" v-model="form.username" type="text" placeholder="Choose a username" />
        </div>
        <div>
          <label for="email">Email</label>
          <input id="email" v-model="form.email" type="email" placeholder="you@example.com" />
        </div>
        <div>
          <label for="phone">Phone</label>
          <input id="phone" v-model="form.phone" type="tel" placeholder="+1 (555) 123-4567" />
        </div>
        <div>
          <label for="password">Password</label>
          <input id="password" v-model="form.password" type="password" placeholder="Create a password" />
        </div>
        <div>
          <label for="confirm">Confirm password</label>
          <input id="confirm" v-model="form.confirm_password" type="password" placeholder="Confirm password" />
        </div>
        <div>
          <label>
            <input v-model="form.terms" type="checkbox" /> I agree to the terms
          </label>
        </div>
        <div class="form-actions">
          <button class="button" type="submit" :disabled="loading">
            {{ loading ? 'Creating...' : 'Create account' }}
          </button>
          <NuxtLink class="button secondary" to="/login">Back to login</NuxtLink>
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
  full_name: '',
  username: '',
  email: '',
  phone: '',
  password: '',
  confirm_password: '',
  terms: false,
});

const loading = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

const submitSignup = async () => {
  errorMessage.value = '';
  successMessage.value = '';

  if (!form.username || !form.email || !form.phone || !form.password || !form.confirm_password) {
    errorMessage.value = 'All fields are required.';
    return;
  }

  if (form.password !== form.confirm_password) {
    errorMessage.value = 'Passwords do not match.';
    return;
  }

  if (!form.terms) {
    errorMessage.value = 'You must agree to the terms.';
    return;
  }

  loading.value = true;
  try {
    const body = new URLSearchParams({
      username: form.username,
      email: form.email,
      phone: form.phone,
      full_name: form.full_name,
      password: form.password,
      confirm_password: form.confirm_password,
      role: 'passenger',
      terms: form.terms ? 'on' : '',
    });

    const response = await fetch(`${apiBase}/signup`, {
      method: 'POST',
      body,
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error('Signup failed');
    }

    successMessage.value = 'Account created. Redirecting to login...';
    await navigateTo('/login');
  } catch (error) {
    errorMessage.value = 'Unable to create account. Please try again.';
  } finally {
    loading.value = false;
  }
};
</script>
