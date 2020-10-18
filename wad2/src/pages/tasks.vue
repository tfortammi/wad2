<template>
  <div class="container">
    <div class="row">
      <div class="col">
        <NavBar></NavBar>
      </div>
    </div>

    <div class="row justify-content-md-center">
        <div class="col-2">
            <Level></Level>
        </div>
        <div class="col-10" style="margin-left: -20px">
            <Character id="ch"></Character>
        </div>
    </div>

    <div class="row justify-content-md-center">
        <div class="col-2" id="sidebar" >
            <button>Create Meeting</button>
        </div>
        <div class="col-10" style="margin-left: -20px">
            <button @click="demoViewMode('day')">Day View Mode</button>
            <button @click="demoViewMode('week')">Week View Mode</button>
            <button @click="demoViewMode('month')">Month View Mode</button>
            <frappe-gantt
            :view-mode="mode"
            :tasks="tasks"
            @task-updated="debugEventLog.push($event)"
            @task-date-updated="debugEventLog.push($event)"
            @task-progress-change="debugEventLog.push($event)"
            />
            <h3>
            TODO: When the Frappe Chart component emits task changes from user
            clicking or dragging make sure to then update the task list passed in
            via prop (App.vue)
            </h3>
            <button @click="addRandomTask">Add</button>
            <div>
            <h5>
                These are the events being emitted by the Vue.js component wrapper
                for Frappe Gantt
            </h5>
            <ul>
                <li v-for="event in debugEventLog" :key="event.id">
                {{ event }}
                </li>
            </ul>
            </div>
        </div>
    </div>
  </div>
</template>

<script>
import FrappeGantt from "../components/Gantt.vue";
import uuidv4 from "uuid/v4";
import NavBar from "../components/NavBar.vue";
import Character from "../components/Character.vue";
import Level from "../components/Level.vue";

export default {
  name: "Tasks",
  props: {},
  components: {
    FrappeGantt,
    NavBar,
    Character,
    Level,
  },
  data() {
    return {
      mode: "week",
      tasks: [
        {
          id: "1",
          name: "Hello",
          start: "2019-01-01",
          end: "2019-01-05",
          progress: 10,
        },
        {
          id: "2",
          name: "World",
          start: "2019-01-05",
          end: "2019-01-10",
          progress: 20,
          dependencies: "1",
        },
        {
          id: "3",
          name: "From",
          start: "2019-01-10",
          end: "2019-01-15",
          progress: 30,
          dependencies: "2",
        },
        {
          id: "4",
          name: "Lloyd",
          start: "2019-01-15",
          end: "2019-01-20",
          progress: 40,
          dependencies: "3",
        },
      ],
      debugEventLog: [],
    };
  },
  methods: {
    addRandomTask() {
      const id = uuidv4();
      this.tasks.push({
        id: id,
        name: id,
        start: "2019-01-01",
        end: "2019-01-05",
        progress: Math.random() * 100,
      });
    },
    demoViewMode(viewMode) {
      this.mode = viewMode;
    },
  },
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

#sidebar {
    border: 2px black solid;
}
</style>
