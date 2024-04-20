import {
  CustomBaseInput,
  CustomSideBar,
  CustomDropDown,
  CustomRange,
  SwitchButton,
  FileInput,
  Card,
  CustomTable
} from "../components/index";


const GlobalComponents = {
  install(Vue) {
    Vue.component(CustomBaseInput.name, CustomBaseInput);
    Vue.component(CustomSideBar.name, CustomSideBar);
    Vue.component(CustomDropDown.name, CustomDropDown);
    Vue.component(FileInput.name, FileInput);
    Vue.component(CustomRange.name, CustomRange);
    Vue.component(CustomTable.name, CustomTable);
    Vue.component(SwitchButton.name, SwitchButton);
    Vue.component(Card.name, Card);
  },
};

export default GlobalComponents;
