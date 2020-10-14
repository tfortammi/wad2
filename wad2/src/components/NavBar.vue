<template>
  <div class="container-fluid">
    <div class="row">
      <div class="col">
        <b-navbar toggleable="lg" type="dark" variant="info">
          <b-navbar-brand href="#">NavBar</b-navbar-brand>

          <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

          <b-collapse id="nav-collapse" is-nav>
            <b-navbar-nav>
              <b-nav-item href="#">Home</b-nav-item>
              <b-nav-item href="#">Tasks</b-nav-item>
              <b-nav-item href="#">Team</b-nav-item>
              <b-nav-item href="#">Profile</b-nav-item>
            </b-navbar-nav>
          </b-collapse>
        </b-navbar>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "NavBar",
  props: {},
};
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
