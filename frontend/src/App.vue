<template>
  <div id="app">
    <router-view/>
  </div>
</template>

<style lang="scss">
#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

// Custom Bootstrap overrides
:root {
  --bs-primary: #0d6efd;
  --bs-success: #198754;
  --bs-danger: #dc3545;
}
</style>