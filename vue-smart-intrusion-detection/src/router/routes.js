import HomeLayout from "@/layout/HomeLayout.vue";
import NotFound from "@/pages/NotFoundPage.vue";

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
  { path: "*", component: NotFound },
];


export default routes;
