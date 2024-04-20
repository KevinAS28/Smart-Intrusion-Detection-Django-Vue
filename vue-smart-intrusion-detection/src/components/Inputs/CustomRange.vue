<template>
  <div class="custom-range-input">
    <b-form-input :id="`type-range`" v-model="value" type="range" :min="min" :max="max" :step="step"
      @input="inputChange"></b-form-input>
    <div style="text-align:center;">{{ valueText }}{{ (value * 100).toFixed(2) }}%</div>
  </div>
</template>

<script>
import { BFormInput } from 'bootstrap-vue';

export default {
  inheritAttrs: true,
  name: "custom-range-input",
  components: {
    BFormInput
  },
  props: {
    min: {
      type: Number,
      required: false,
      default: 0
    },

    max: {
      type: Number,
      required: false,
      default: 1
    },

    step: {
      type: Number,
      required: false,
      default: 0.05
    },

    valueText: {
      type: String,
      required: false,
      default: "Value: "
    },
    storeInputName: {
      type: String,
      default: 'thrh',
      required: false
    }


  },
  data() {
    return {
      value: '0.5'
    };
  },
  mounted() {
  },
  methods: {
    async fetchItems() {
      try {

      } catch (error) {
        console.error('Error fetching items:', error);
      }
    },

    inputChange() {
      this.$emit('store-input', "inference", this.storeInputName, parseFloat(this.value));
    },

  },
};
</script>

<style scoped>
.custom-range-input div {
  position: relative;
  left: 0;
  top: 0;
}

.custom-range::-moz-range-thumb {
  background-color: #6484d5;

}

/* Optional styling for the dropdown */
</style>
