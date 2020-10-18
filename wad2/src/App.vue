<template>
    <div id="app">
        <router-view/>
        
    </div>
</template>

<script>
export default {
    name: 'App',
    components: {
    }};
</script>

<style>
@import "../node_modules/frappe-gantt/dist/frappe-gantt.css";

#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
  margin-top: 60px;
}
</style>