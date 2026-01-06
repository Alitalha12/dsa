<template>
  <div class="app-shell">
    <aside class="sidebar">
      <NuxtLink class="logo" to="/">ITRS Dashboard</NuxtLink>
      <nav>
        <NuxtLink to="/">Overview</NuxtLink>
        <NuxtLink to="/admin-dashboard">Admin</NuxtLink>
        <NuxtLink to="/admin-routes">Routes</NuxtLink>
        <NuxtLink to="/admin-bus-management">Buses</NuxtLink>
        <NuxtLink to="/passenger-dashboard">Passenger</NuxtLink>
        <NuxtLink to="/sim-dashboard">Simulation</NuxtLink>
        <NuxtLink to="/status">API Status</NuxtLink>
        <NuxtLink to="/login">Login</NuxtLink>
      </nav>
    </aside>

    <div class="main-content">
      <header class="topbar">
        <div>
          <h1>Intelligent Transport System</h1>
          <p class="subtitle">Operational dashboard powered by Python APIs.</p>
        </div>
        <div class="form-actions">
          <NuxtLink class="button secondary" to="/signup">Create account</NuxtLink>
          <NuxtLink class="button" to="/login">Sign in</NuxtLink>
        </div>
      </header>

      <main class="page">
        <slot />
      </main>

      <footer class="footer">
        <div class="container">
          <p>Nuxt UI dashboard for the Intelligent Transport Routing & Simulation system.</p>
        </div>
      </footer>
    </div>
  </div>
</template>
