<template>
    <div class="custom-base-input " >  
        <b-form-input 
        v-model="text" 
        :placeholder="placeholder"
        :type="type"
        />
    </div>
  </template>
  
  <script>
  import { BFormInput } from 'bootstrap-vue';
  
  export default {
    inheritAttrs: true,
    name: "custom-base-input",  
    components: {
      BFormInput
    },
    props: {
      type: {
        type: String,
        required: false,
        default: "text"
      },      
      placeholder: {
        type: String,
        required: false,
        default: ""
      },
      size: {
        type: String,
        required: false,
        default: ""
      },
      state: {
        type: String,
        required: false,
        default: "null"
      },      
      storeInputName: {
          type: String,
          default: 'model_name',
          required: false
      } 
      
    },  
    data() {
      return {
        text: "",
        allItems: [{"id": 1, "name": "No other items"}]
      };
    },
    mounted() {
      // this.fetchItems(); // Fetch items on component mount
      // this.items = JSON.parse(this.items);
      if (this.stringItems.length>0) {
        console.log('dropdown use from string');
        this.allItems = JSON.parse(this.stringItems);
      } else if (this.listItems!=null){
        console.log('dropdown use from list');
        this.allItems = this.listItems;
      } else if (this.urlItems.length>0) {
        console.log('dropdown use from url ' + this.urlItems );
        this.fetchItemsFromURL(this.urlItems);
      } else {
        console.log('dropdown no items ', this.listItems);
        this.allItems = [{"id": 1, "name": "No other items"}];
      }
      if (this.text=="Choose"){
          this.finaltext = this.allItems[0]["name"];
      }    
      console.log("allItems:", this.allItems);
    },
    methods: {
      async fetchItemsFromURL(url) {
        try {
          const response = await fetch(url);
          const data = await response.json();
          this.allItems = data;
        } catch (error) {
          console.error('Error fetching items:', error);
        }
      },
      selectItem(item) {
        // Handle item selection (e.g., display selected item or perform actions)
        console.log('Selected item:', item);
        this.$emit('store-input', "inference", this.storeInputName, item.name);
        this.finaltext = item.name;
      },
    },
  };
  </script>
  
  <style scoped>
  .custom-base-input div{
    position: relative;
    left:0;
    top:0;
  }
  

  </style>
  