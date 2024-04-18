<template>
    <div class="file-uploader">
        <label for="fileInput">Select File:</label>
        
        <b-form-file id="file-default" v-model="selectedFile" :value="selectedFile" ref="file-input" @change="handleFileChange" :file-name-formatter="formatNames"/>
        <!-- <b-button v-if="selectedFile" variant="outline-dark" @click="uploadFile()">Upload</b-button> -->

        <!-- <input type="file" id="fileInput" ref="fileInput" @change="handleFileChange" multiple> -->
        <!-- <p v-if="selectedFile">Selected file: {{ selectedFile.name }}</p>  -->
        <!-- <b-button v-if="selectedFile" variant="outline-dark" @click="uploadFile()">Upload</b-button> -->
        <!-- <button v-if="selectedFile" @click="uploadFile">Upload</button> -->
        <!-- <div class="dropzone" @dragover.prevent @drop.prevent="handleDragDrop">
            Drag & Drop files here
        </div> -->
    </div>
</template>

<script>
import { BFormFile } from 'bootstrap-vue';

export default {
    inheritAttrs: false,
    name: 'file-input',
    components: {
        BFormFile
    },
    props:{
      storeInputName: {
        type: String,
        default: 'input_file',
        required: false
      }  
    },
    data() {
        return {
            selectedFile: null,  
        };
    },
    methods: {
        // inputGetter(key, value){
        //     console.log("default inputGetter");
        // },
        // storeInput(method){
        //     method("file", this.selectedFile);
        // },
        handleFileChange(event) {
            console.log("file changed");
            this.selectedFile = event.target.files[0]; // Get the first selected file            
            this.$emit('store-input', "file", this.storeInputName, this.selectedFile);
            this.$emit('store-input', "backend_view", "new_video_file", true);
            
        },

        uploadFile() {
            console.log(this.selectedFile.name );

        },
        formatNames(files) {
            if (files.length==1){
                return files[0].name
            }
            else if (files.length==0){
                return 'No file selected';
            }
            else{
                return `${files.length} files selected`;
            }
      }        
    },
};
</script>

<style scoped>
.file-uploader {
    /* Add your styling for the component */
}

.dropzone {
    border: 2px dashed #ccc;
    padding: 10px;
    text-align: center;
}
</style>