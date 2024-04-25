import HomeLayout from "@/layout/HomeLayout.vue";
import NotFound from "@/pages/NotFoundPage.vue";
import Login from "@/pages/Login.vue"
const Home = () =>
  import("@/pages/Home.vue");

const routes = [
  {
    path: "/",
    component: HomeLayout,
    redirect: "/home",
    children: [
      {
        path: "home",
        name: "home",
        component: Home,
      },

    ],
  },
  {
    path: "/login",
    component: Login,

  },
  { path: "*", component: NotFound },
];


export default routes;
