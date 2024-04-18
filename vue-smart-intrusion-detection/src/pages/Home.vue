<template>
  <div>
    <div class="row">
      <div class="col-12">
        <card type="chart">
          <template slot="header">
            <div class="row">
              <div class="col-sm-6" :class="isRTL ? 'text-right' : 'text-left'">
                <!-- <h5 class="card-category">
                  {{ $t("dashboard.totalShipments") }}
                </h5> -->
                <h2 class="card-title">Live Camera</h2>
              </div>
              <!-- <div class="col-sm-6">
                <div
                  class="btn-group btn-group-toggle"
                  :class="isRTL ? 'float-left' : 'float-right'"
                  data-toggle="buttons"
                >
                  <label
                    v-for="(option, index) in bigLineChartCategories"
                    :key="option"
                    class="btn btn-sm btn-primary btn-simple"
                    :class="{ active: bigLineChart.activeIndex === index }"
                    :id="index"
                  >
                    <input
                      type="radio"
                      @click="initBigChart(index)"
                      name="options"
                      autocomplete="off"
                      :checked="bigLineChart.activeIndex === index"
                    />
                    {{ option }}
                  </label>
                </div>
              </div> -->
            </div>
          </template>
          <div style="text-align: center;">
            
            <img class="camera-stream" style="-webkit-user-select: none;"
              :src="'http://localhost:8001/intrusion-detection/videostream/?token=' + token + '&last_settings_updated='+last_settings_updated" 
              :style="{ width: camImageWidth + 'px', height: camImageHeight + 'px' }">
            <div class="cam-controls">
              <b-button variant="outline-dark" @click="camZoomIn">Zoom In</b-button>
              <b-button variant="outline-dark" @click="camZoomOut">Zoom Out</b-button>
              <!-- <button @click="camZoomIn">Zoom In</button> -->
              <!-- <div style="width:100px;"></div> -->

            </div>
          </div>
        </card>
      </div>
    </div>
    <b-button variant="outline-dark" @click="updateSettings()"
      style="text-align:center; position:relative; display:block; margin-left:auto; margin-right:auto; margin-bottom: 10px;">Update
      All Settings</b-button>
    <div class="row">
      <div class="col-4">
        <card type="chart">
          <template slot="header">
            <h5 class="card-category"></h5>
            <h3 class="card-title">
              <i class="tim-icons icon-atom text-info"></i>
              Model Control
            </h3>
            <div class="chart-area" style="padding:20px;display: block;">
              <p style="position:relative;width:fit-content;">Choose ML model</p>
              <custom-dropdown-input text="RTDETR-YoloV9EBB-27ep"
                url-items="http://localhost:8001/intrusion-detection/modellist/"
                @store-input="getInput"
                store-input-name="model_name"
                />
              <hr style="position:relative;margin-top: 25px; margin-bottom: 25px;height:1px;background-color: white;" />
              <!-- <div style="position:relative;margin-top: 15px; margin-bottom: 15px;"></div> -->
              <p style="position:relative;width:fit-content;">Adjust Confidence Threshold</p>
              <custom-range-input @store-input="getInput" store-input-name="thrh" style="position:relative;" value-text="Threshold value: "/>
            </div>
          </template>
          <!-- <div class="chart-area">
            <line-chart style="height: 100%" chart-id="purple-line-chart" :chart-data="purpleLineChart.chartData"
              :gradient-colors="purpleLineChart.gradientColors" :gradient-stops="purpleLineChart.gradientStops"
              :extra-options="purpleLineChart.extraOptions">
            </line-chart>
          </div> -->
        </card>
      </div>

      
      
      <div class="col-lg-4" :class="{ 'text-right': isRTL }">
        <card type="chart">
          <template slot="header">
            <h5 class="card-category"></h5>
            <h3 class="card-title">
              <i class="tim-icons icon-bell-55 text-info"></i> Alarm
            </h3>
          </template>

          <div class="chart-area" style="padding:20px;display: block; height:fit-content;">
            <p style="position:relative; width:fit-content; display:inline-block;">Segmentation orientation</p>
            <custom-dropdown-input style="position:relative;" text="Horizontal"
              :list-items='line_orientation_list' 
              @store-input="getInput"
              store-input-name="line_orientation"
              />

            <hr style="position:relative;margin-top: 25px; margin-bottom: 25px;height:1px; background-color: white;" />
            <p style="position:; width:100%; display:inline-block;text-align:center;">Point 1</p>
            <div>
              <div style="float: left; width:50%; padding-left:30px; position:relative;">
                <p style="position:relative; width:fit-content; display:inline-block; right:20px;">X:</p>
                <b-form-input v-model="point1X" :id="`type-number`" type="number" min="0" max="640"
                  style="width: 80%;display:inline;position:relative; background-color:rgba(0,0,0,0);"></b-form-input>
                
              </div>
              <div style="float: right; align: right; width:50%; padding-left:30px; position:relative; display:inline;">
                <p style="position:relative; width:fit-content; display:inline-block; right:20px; background-color:rgba(0,0,0,0);">Y:</p>
                <b-form-input v-model="point1Y" :id="`type-number`" type="number" min="0" max="640"
                  style="width: 80%;display:inline;position:relative; background-color:rgba(0,0,0,0);"></b-form-input>
              </div>
            </div>

      
            <!-- <p style="position:relative; width:100%; display:inline-block;text-align:center; margin-top:30px;">Point 2</p>
            <div>
              <div style="float: left; width:50%; padding-left:30px; position:relative;">
                <p style="position:relative; width:fit-content; display:inline-block; right:20px;">X:</p>
                <b-form-input v-model="point2X" :id="`type-number`" type="number" min="0" max="640" default="640"
                  style="width: 80%;display:inline;position:relative; background-color:rgba(0,0,0,0);"></b-form-input>
              </div>
              <div style="float: right; align: right; width:50%; padding-left:30px; position:relative; display:inline;">
                <p style="position:relative; width:fit-content; display:inline-block; right:20px;">Y:</p>
                <b-form-input v-model="point2Y" :id="`type-number`" type="number" min="0" max="640" default="450"
                  style="width: 80%;display:inline;position:relative; background-color:rgba(0,0,0,0);"></b-form-input>
              </div>
            </div> -->

            <div style="width:100%;margin-top:50px;display:block;position:relative;">
              <p style="position:relative; width:fit-content; display:block; text-align:center; width:100%;"> Flip Area
              </p>
              <custom-switch-button items='["Not flipped", "Flipped"]' text="Flip Area"
                style="text-align:center; position:relative; display: block; margin-left: auto; margin-right: auto;" 
                @store-input="getInput"
                store-input-name="invert_line"
                />
            </div>
            <hr style="position:relative;margin-top: 25px; margin-bottom: 25px;height:1px;background-color: white;" />
          </div>
        </card>
      </div>

      <div class="col-lg-4" :class="{ 'text-right': isRTL }">
        <card type="chart">
          <template slot="header">
            <h5 class="card-category"></h5>
            <h3 class="card-title">
              <i class="tim-icons icon-tv-2 text-success"></i> Video Settings
            </h3>
          </template>
          <div class="chart-area">
            <file-input @store-input="getInput" store-input-name="video_file" />
          </div>
        </card>
      </div>
    

    </div>
  </div>
</template>
<script>


export default {
  props: {
    camInitialWidth: {
      type: Number,
      default: 450,
    },
    camInitialHeight: {
      type: Number,
      default: 450, // Adjust default height as needed
    },
    camZoomFactor: {
      type: Number,
      default: 1.2, // Adjust zoom factor (e.g., for more gradual zoom)
    },
    camMinZoom: {
      type: Number,
      default: 150, // Set minimum image width/height
    },
    
  },
  components: {

  },
  data() {
    return {
      token: "165805894906728e2813aa9c700155c3299e040df9a94958251514b8aca4db25143bca0caa5d01edb5fb3e35a64e1857",

      camImageWidth: this.camInitialWidth,
      camImageHeight: this.camInitialHeight,
      camIsMinZoom: false,
      modelListItems: [],
      line_orientation_list: [{"id": 1, "name": "Horizontal"}, {"id": 2, "name": "Vertical"}],
      newSettings: {
        'inference': {

        },
        'backend_view': {
            'new_video_file': false
        }
      },
      newFiles: {
          "video_file": false
      },

      dynamic: {

      },

      point1X: 0,
      point1Y: 450,
      point2X: 640,
      point2Y: 450,
      line_orientation: 'Horizontal',
      last_settings_updated: Date.now()
    };
  },
  computed: {
    enableRTL() {
      return this.$route.query.enableRTL;
    },
    isRTL() {
      return this.$rtl.isRTL;
    },
  },
  methods: {
    getInput(group, key, value) {
      if (group=="file"){
        this.newFiles[key] = value;
      } else{
        this.newSettings[group][key] = value;
        console.log("getInput(): "+ key);
        console.log(this.newSettings);
      }
    },

    camZoomIn() {
      this.camImageWidth *= this.camZoomFactor;
      this.camImageHeight *= this.camZoomFactor;
      this.camIsMinZoom = this.camImageWidth <= this.minZoom || this.camImageHeight <= this.camMinZoom;
    },
    camZoomOut() {
      this.camImageWidth /= this.camZoomFactor;
      this.camImageHeight /= this.camZoomFactor;
      this.camIsMinZoom = this.camImageWidth <= this.minZoom || this.camImageHeight <= this.camMinZoom;
    },
    async formHitAPI(url, body, key) {
      try {
        const response = await fetch(url); // Replace with your API URL
        const data = await response.json();
        this.dynamic[key] = data;
      } catch (error) {
        this.dynamic[key] = error;
        console.error('Error fetching data:', error);
        // Handle errors appropriately, e.g., display an error message to the user
      }
    },
    updateSettings() {
      const formData = new FormData();

      let line = `${this.line_orientation[0].toLowerCase()}_${this.point1X}_${this.point1Y}_${this.newSettings["inference"]["invert_line"]}`;
      this.newSettings["inference"]["overlay_line"] = line;
      console.log("line", line);
      
      formData.append("new_settings", JSON.stringify(this.newSettings));  
      for (const [key, value] of Object.entries(this.newFiles)) {
        console.log("adding file " + key + " to form");
        formData.append(key, value);  
      }

      // const headers = new Headers();
      // headers.append('Content-Type', 'multipart/form-data; boundary=---------------------------77135198018380622703317445938');
      // headers.append('Host', 'localhost:8001');
      // headers.append('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/109.0');
      // headers.append('Accept', '*/*');
      // headers.append('Accept-Language', 'en-US,en;q=0.5');
      // headers.append('Accept-Encoding', 'gzip, deflate, br');
      // headers.append('Referer', 'http://localhost:8080/');
      // headers.append('Origin', 'http://localhost:8080');
      // headers.append('Connection', 'keep-alive');
      // headers.append('Sec-Fetch-Dest', 'empty');
      // headers.append('Sec-Fetch-Mode', 'cors');
      // headers.append('Sec-Fetch-Site', 'same-site');
      // headers.append('Pragma', 'no-cache');
      // headers.append('Cache-Control', 'no-cache');
      // headers.append('token', this.token);

      fetch('http://localhost:8001/intrusion-detection/updatesettings/?token='+this.token, {
        method: 'POST',
        body: formData,
        // headers: headers,
      })
        .then(response => response.json())
        .then(data => {
          console.log('Upload successful:', data);
          this.selectedFile = null;
          this.$forceUpdate();
          this.last_settings_updated = Date.now();
        })
        .catch(error => {
          console.error('Upload failed:', error);
        });
    }

  },
  mounted() {
    this.i18n = this.$i18n;
    if (this.enableRTL) {
      this.i18n.locale = "ar";
      this.$rtl.enableRTL();
    }
  },
  created(){

  },
  beforeDestroy() {
    if (this.$rtl.isRTL) {
      this.i18n.locale = "en";
      this.$rtl.disableRTL();
    }
  },
};

</script>
<style>
.cam-controls {
  margin-top: 10px;
  /* display: flex; */
  text-align: center;
  /* justify-content: space-between; */
}

.cam-controls button {
  padding: 5px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.cam-controls button:disabled {
  opacity: 0.5;
  cursor: default;
}

p {
  color: rgba(255, 255, 255, 0.8);
}

</style>
