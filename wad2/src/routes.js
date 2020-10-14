import Vue from 'vue';
import VueRouter from "vue-router";

// import pages
import Tasks from "@/pages/Tasks.vue";
import Home from "@/pages/Home.vue";


Vue.use(VueRouter)
export default new VueRouter({
  mode: "history",
  routes: [
    {
      path: "/", 
      name: "Home",
      component: Home
    },
    {
      path: "/tasks", 
      name: "Tasks",
      component: Tasks
    }
  ]
})