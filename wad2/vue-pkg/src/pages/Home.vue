<template>
    <div class="container-fluid">
        <div class="row">
        <div class="col">
            <NavBar></NavBar>
            <h1>HOME</h1>
            <line-chart></line-chart>
        </div>
        </div>
    </div>
</template>

<script>
import NavBar from "../components/NavBar.vue";
import LineChart from "../components/LineChart.vue";

export default {
  name: "Home",
  props: {},
  components: {
    NavBar,
    LineChart
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
