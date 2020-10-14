<template>
    <div class="container-fluid">
        <div class="row">
        <div class="col">
            <NavBar></NavBar>
            <h1>HOME</h1>

        </div>
        </div>
    </div>
</template>

<script>
import NavBar from "../components/NavBar.vue";

export default {
  name: "Home",
  props: {},
  components: {
    NavBar
  }
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
