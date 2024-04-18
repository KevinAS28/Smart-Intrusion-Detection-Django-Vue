<template>
    <b-button :variant="variant" @click="selectItem()">{{ finalText }}</b-button>
</template>

<script>
import { BButton } from 'bootstrap-vue';

export default {
  inheritAttrs: true,
  name: "custom-switch-button",  
  components: {
    BButton
  },
  props: {
    text: {
      type: String,
      required: true,
      default: "Switch"
    },
    variant: {
      type: String,
      required: false,
      default: "outline-dark"
    },
    items: {
      type: String,
      required: true
    },
    storeInputName: {
        type: String,
        default: 'model_name',
        required: false
    }      
  },  
  data() {
    return {
        selectedIndex: 0,
        allItems: JSON.parse(this.items),
        finalText: this.text,
        
        
    };
  },
  mounted() {
    this.finalText = this.text + ": " + this.allItems[this.selectedIndex];
    this.$emit('store-input', "inference", this.storeInputName, this.selectedIndex);
  },
  methods: {
    selectItem() {
        if (Object.keys(this.allItems).length-1==this.selectedIndex){
            this.selectedIndex = 0;
        } else {
            this.selectedIndex++;
        }
        this.finalText = this.text + ": " + this.allItems[this.selectedIndex];
        this.$emit('store-input', "inference", this.storeInputName, this.selectedIndex);

    },
  },
};
</script>

<style scoped>



/* Optional styling for the dropdown */
</style>
