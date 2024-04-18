import {
  CustomBaseInput,
  CustomDropDown,
  CustomRange,
  SwitchButton,
  FileInput,
  Card,
} from "../components/index";


const GlobalComponents = {
  install(Vue) {
    Vue.component(CustomBaseInput.name, CustomBaseInput);
    Vue.component(CustomDropDown.name, CustomDropDown);
    Vue.component(FileInput.name, FileInput);
    Vue.component(CustomRange.name, CustomRange);
    Vue.component(SwitchButton.name, SwitchButton);
    Vue.component(Card.name, Card);
  },
};

export default GlobalComponents;
