<template>
  <div class="container-fluid" id="lvl-container">
    <div class="row">
      <div class="col" id="window">
        <h1>Level 20</h1>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Level",
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

#lvl-container {
  width: 150px;
  padding: 0px;
}

#window {
  border: 2px solid black;
  height: 120px;
}

</style>
