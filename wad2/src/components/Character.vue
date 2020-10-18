<template>
  <div class="container-fluid" id="ch-container">
    <div class="row">
      <div class="col" id="window">
        <img id="ch-img" src="../assets/knight.png">
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: "Character",
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

#ch-container {
  width: 80%;
}

#window {
  border: 2px solid black;
  background-image: url("../assets/wall.png");
  background-size: 120px;
  height: 120px;
}

#ch-img {
  width: 70px;
  margin-top: -15px;
  margin-left: 10px;
}
</style>
