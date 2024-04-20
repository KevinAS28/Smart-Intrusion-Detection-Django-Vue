<template>
  <div>
    <div>
      <b-alert variant="danger" show dismissible @dismissed="closeNotification" v-model="showNotification"
        style="position:fixed;z-index: 2;color:white; background-color:rgba(217,67,85,1); left: 50%; transform: translate(-50%, 20%);">
        <h5 class="font-weight-bold"> Objects Crossed the Line</h5>
        <p>{{ notificationText }}</p>
        <p class="text-muted mb-0"> 19:08:01 </p>
      </b-alert>
      <div>
        <template>
          <b-sidebar v-model="showSidebar" right bg-variant="dark" text-variant="light" title="Sidebar Title" shadow>

            <div class="col px-3 py-2" v-show="showSettingsContent">
              <p>
                SETTINGS
              </p>
              <custom-table :itemList="sideBarTableItems" />
            </div>

            <div class="px-3 py-2" v-show="showNotificationContent">

              <template>

                <div>
                  <div v-for="(imgUrl, index) in warningImgs" :key="index" class="row">
                    <div class="col-sm">
                      <card type="primary">
                        <div class="row">
                          <div class="" :class="isRTL ? 'text-right' : 'text-left'">
                            <div style="width:100%;text-align:center;">
                              <img :src="imgUrl" alt="Warning Image" class="img-fluid" style="width:60%;" />
                            </div>

                          </div>
                        </div>
                      </card>
                    </div>
                  </div>
                </div>
              </template>
            </div>

          </b-sidebar>
        </template>
      </div>
      <div
        style="position:fixed; z-index: 1;background-color: rgb(29, 29, 45); width:100%; box-shadow: 0px 15px 10px rgba(0, 0, 0, 0.2);">
        <b-navbar toggleable="lg" type="dark" style="padding:10px; padding-left:30px; padding-right:30px;">
          <b-navbar-brand href="#">
            <p class="h1" style="color:white;">Smart Intrusion Detection</p>
          </b-navbar-brand>

          <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>

          <b-collapse id="nav-collapse" is-nav>
            <b-navbar-nav>
              <!-- <b-nav-item href="#">Link</b-nav-item>
            <b-nav-item href="#" disabled>Disabled</b-nav-item> -->
            </b-navbar-nav>

            <b-navbar-nav class="ml-auto">
              <b-nav-item href="#" @click="toggleSettingsSidebar">
                <b-icon icon="table"></b-icon>
                Show Inference Settings
              </b-nav-item>
              <b-nav-item href="#" @click="toggleNotifSidebar">
                <b-icon icon="bell"></b-icon>
                Notifications
              </b-nav-item>
              <!-- <b-nav-form>
              <b-form-input size="sm" class="mr-sm-2" placeholder="Search"></b-form-input>
              <b-button size="sm" class="my-2 my-sm-0" type="submit">Search</b-button>
            </b-nav-form> -->

              <!-- <b-nav-item-dropdown text="Lang" right>
              <b-dropdown-item href="#">EN</b-dropdown-item>
              <b-dropdown-item href="#">ES</b-dropdown-item>
              <b-dropdown-item href="#">RU</b-dropdown-item>
              <b-dropdown-item href="#">FA</b-dropdown-item>
            </b-nav-item-dropdown> -->

              <!-- <b-button v-b-toggle.sidebar-right variant="outline-light"
              style="background-color: rgba(0,0,0,0);color:white;">Toggle
              Sidebar</b-button> -->
              <b-nav-item-dropdown right>

                <template #button-content>
                  <em>User</em>
                </template>
                <b-dropdown-item href="#">Profile</b-dropdown-item>
                <b-dropdown-item href="#">Sign Out</b-dropdown-item>
              </b-nav-item-dropdown>
            </b-navbar-nav>
          </b-collapse>
        </b-navbar>
      </div>
    </div>
    <!-- <b-alert show dismissible @dismissed="closeNotification" v-model="showNotification"  variant="info"  style="position:fixed;z-index: 1;color:white; background-color:rgba(217,67,85,1); left: 50%; transform: translate(-50%, 30%);" >
        {{ notificationText }}
    </b-alert> -->
    <div id="home_content_body" style="padding:30px; padding-top:100px;">
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

              <img class="camera-stream" style="-webkit-user-select: none;" ref="videoElement"
                :src="'http://localhost:8001/intrusion-detection/videostream/?token=' + token + '&last_settings_updated=' + last_settings_updated"
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
                <p style="position:relative; width:100%; display:inline-block;text-align:center;">Choose ML model</p>
                <custom-dropdown-input url-items="http://localhost:8001/intrusion-detection/modellist/"
                  @store-input="getInput" store-input-name="model_name" listenerName="choose_model" text="Choose"
                  style="text-align: center;" />
                <hr style="position:relative;margin-top: 25px; margin-bottom: 25px;height:1px;background-color: white;" />
                <!-- <div style="position:relative;margin-top: 15px; margin-bottom: 15px;"></div> -->
                <p style="position:relative; width:100%; display:inline-block;text-align:center;">Adjust Confidence
                  Threshold</p>
                <custom-range-input @store-input="getInput" store-input-name="thrh" style="position:relative;"
                  value-text="Threshold value: " />
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
              <p style="position:relative; width:100%; display:inline-block;text-align:center;">Segmentation orientation
              </p>
              <custom-dropdown-input style="position:relative;text-align:center;" :list-items='line_orientation_list'
                @store-input="getInput" store-input-name="line_orientation" />

              <hr style="position:relative;margin-top: 25px; margin-bottom: 25px;height:1px; background-color: white;" />
              <p style="position:; width:100%; display:inline-block;text-align:center;">Line Point</p>
              <div>
                <div style="float: left; width:50%; padding-left:30px; position:relative;">
                  <p style="position:relative; width:fit-content; display:inline-block; right:20px;">X:</p>
                  <b-form-input v-model="point1X" :id="`type-number`" type="number" min="0" max="640"
                    style="width: 80%;display:inline;position:relative; background-color:rgba(0,0,0,0);"
                    :disabled="disabledPoint1X"></b-form-input>

                </div>
                <div style="float: right; align: right; width:50%; padding-left:30px; position:relative; display:inline;">
                  <p
                    style="position:relative; width:fit-content; display:inline-block; right:20px; background-color:rgba(0,0,0,0);">
                    Y:</p>
                  <b-form-input v-model="point1Y" :id="`type-number`" type="number" min="0" max="640"
                    style="width: 80%;display:inline;position:relative; background-color:rgba(0,0,0,0);"
                    :disabled="disabledPoint1Y"></b-form-input>
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
                  @store-input="getInput" store-input-name="invert_line" />
              </div>
              <hr style="position:relative;margin-top: 25px; margin-bottom: 25px;height:1px;background-color: white;" />
              <b-form-input v-model="objects_to_warn" :id="`type-text`" type="text"
                style="width: 50%;text-align:center; position:relative; display: block; margin-left: auto; margin-right: auto; background-color:rgba(0,0,0,0);"></b-form-input>
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
  </div>
</template>
<script>
import moment from 'moment';
import 'moment-timezone';


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

      showSidebar: false,
      sidebarTitle: "Inference Settings",
      showSettingsContent: false,
      showNotificationContent: false,

      notificationText: "Nothing",
      showNotification: false,

      camImageWidth: this.camInitialWidth,
      camImageHeight: this.camInitialHeight,
      camIsMinZoom: false,
      modelListItems: [],
      modelName: "",
      sideBarTableItems: [{ "col1": 1, "col2": 2 }, { "col1": 3, "col2": 4, "col3": 5 }],

      line_orientation_list: [{ "id": 1, "name": "Horizontal" }, { "id": 2, "name": "Vertical" }],
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
      // modelName: "",
      point1X: 0,
      point1Y: 0,
      disabledPoint1X: true,
      disabledPoint1Y: true,

      last_settings_updated: Date.now(),
      objects_to_warn: 'person,bicycle',
      warningImgs: []
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
      if (group == "file") {
        this.newFiles[key] = value;
      } else {
        this.newSettings[group][key] = value;
        console.log("getInput(): " + key + " " + value);
        console.log(this.newSettings);

        if (key == "line_orientation") {
          if (value[0].toLowerCase() == "v") {
            this.disabledPoint1Y = true;
            this.point1Y = 0;
            this.disabledPoint1X = false;

          } else {
            this.disabledPoint1Y = false;
            this.disabledPoint1X = true;
            this.point1X = 0;
          }
        }
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

    updateSettings() {
      const formData = new FormData();

      if (("line_orientation" in this.newSettings["inference"])) {
        let line = `${this.newSettings["inference"]["line_orientation"][0].toLowerCase()}_${this.point1X}_${this.point1Y}_${this.newSettings["inference"]["invert_line"]}`;
        console.log("line", line);
        this.newSettings["inference"]["overlay_line"] = line;
        this.newSettings["inference"]["objects_to_warn"] = this.objects_to_warn;

      }
      else {
        console.log("No new line");
      }


      formData.append("new_settings", JSON.stringify(this.newSettings));
      for (const [key, value] of Object.entries(this.newFiles)) {
        console.log("adding file " + key + " to form");
        formData.append(key, value);
      }

      fetch('http://localhost:8001/intrusion-detection/updatesettings/?token=' + this.token, {
        method: 'POST',
        body: formData,
        // headers: headers,
      })
        .then(response => response.json())
        .then(data => {
          console.log('Update settings successful:', data);
          this.selectedFile = null;
          console.log("model_name in inference", "model_name" in this.newSettings["inference"]);
          if (this.newSettings['backend_view']['new_video_file'] || "model_name" in this.newSettings["inference"]) {
            this.$forceUpdate();
            this.last_settings_updated = Date.now();
            location.reload();

          }

        })
        .catch(error => {
          console.error('Upload failed:', error);
        });
    },

    async getStatus() {
      try {
        const response = await fetch('http://localhost:8001/intrusion-detection/status/?token=' + this.token);
        if (!response.ok) {
          throw new Error(`API request failed with status ${response.status}`);
        }
        const data = await response.json();
        console.log("status: ", data);
        this.status = data.status;
        if (data['warnings'].length > 0) {

          let warning = data['warnings'][0];
          let notificationTime = moment.utc(warning["updated_at"] * 1000).tz('Asia/Jakarta').format("YYYY-MM-DD HH:mm:ss");;
          this.notificationText = `${notificationTime} Object(s) has crossed the line: ${warning.objs.replace(",", ", ")}`
          console.log("show notification: " + this.notificationText + " " + warning["updated_at"]);
          this.warningImgs[0] = warning["frame_path"];
          this.showNotification = true;
        }

      } catch (error) {
        console.error('Error fetching status:', error);
      }
    },
    closeNotification() {
      this.showNotification = false;
      fetch('http://localhost:8001/intrusion-detection/clearwarning/?token=' + this.token, {
        method: 'GET',
        // headers: headers,
      })
        .then(response => response.json())
        .then(data => {
          console.log("clear warning:", data);
        })
        .catch(error => {
          console.error('clear warning:', error);
        });

    },
    userSettingsToTable(data) {
      const filteredData = {
        inferenceSettings: data.inference_settings,
        homeSetttings: data.home_settings,
      };
      let excludedKeys = ["id", "user"];

      let tableData = [];

      const filteredEntries = Object.entries(filteredData);
      for (let i = 0; i < filteredEntries.length; i++) {
        const [key, value] = filteredEntries[i];
        for (const innerKey in value) {
          if (excludedKeys.includes(innerKey)) {
            continue;
          }
          tableData.push({
            key: innerKey,
            value: value[innerKey],
          });
        }
      }
      return tableData;
    },
    async getUserSettings() {
      this.showNotification = false;
      fetch('http://localhost:8001/intrusion-detection/usersettings/?token=' + this.token, {
        method: 'GET',
        // headers: headers,
      })
        .then(response => response.json())
        .then(data => {
          console.log("user settings:", data);
          this.$emit("choose_model", data["inference_settings"]["model_name"]);
          this.sideBarTableItems = this.userSettingsToTable(data);
          // this.modelName = data["inference_settings"]["model_name"];
          // size = data["inference_settings"]["size"];
          // thrh = data["inference_settings"]["thrh"];
          // overlayLine = data["inference_settings"]["overlay_line"];
          // objectsToWarn = data["inference_settings"]["objects_to_warn"];

        })
        .catch(error => {
          console.error('get user settings:', error);
        });

    },
    toggleSettingsSidebar() {
      console.log("toogle settings sidebar ", this.showSidebar, this.showSettingsContent);
      this.showNotificationContent = false;
      this.showSidebar = !this.showSidebar;
      this.showSettingsContent = this.showSidebar ? true : false;


    },
    toggleNotifSidebar() {
      console.log("toogle notif sidebar ", this.showSidebar, this.showNotificationContent);
      this.showSettingsContent = false;
      this.showSidebar = !this.showSidebar;
      this.showNotificationContent = this.showSidebar ? true : false;

    }

  },
  mounted() {
    this.i18n = this.$i18n;
    if (this.enableRTL) {
      this.i18n.locale = "ar";
      this.$rtl.enableRTL();
    }
    this.getStatus();
    this.intervalId = setInterval(this.getStatus, 2000);

  },
  created() {
    this.getUserSettings();
  },
  beforeDestroy() {
    if (this.$rtl.isRTL) {
      this.i18n.locale = "en";
      this.$rtl.disableRTL();
    }
    clearInterval(this.intervalId);
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

.b-sidebar {
  width: 40%;
}
</style>
