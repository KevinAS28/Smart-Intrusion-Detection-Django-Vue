<template >
    <div>
        <b-button v-b-toggle.custom-sidebar>Toggle Sidebar</b-button>
        <b-sidebar id="custom-sidebar" aria-labelledby="custom-sidebar-title" no-header shadow :style="theStyle">
            <template #default="{ hide }">
                <div class="p-3 col-md-4">
                    <h4 id="custom-sidebar-title">Custom header sidebar</h4>
                    <p>
                        Cras mattis consectetur purus sit amet fermentum. Cras justo odio, dapibus ac facilisis
                        in, egestas eget quam. Morbi leo risus, porta ac consectetur ac, vestibulum at eros.
                    </p>
                    <nav class="mb-3">
                        <b-nav vertical>
                            <b-nav-item active @click="hide">Active</b-nav-item>
                            <b-nav-item href="#link-1" @click="hide">Link</b-nav-item>
                            <b-nav-item href="#link-2" @click="hide">Another Link</b-nav-item>
                        </b-nav>
                    </nav>
                    <b-button variant="primary" block @click="hide">Close Sidebar</b-button>
                </div>
            </template>
        </b-sidebar>
    </div>
</template>

<script>
import { BSideBar } from 'bootstrap-vue';

export default {
    inheritAttrs: true,
    name: "custom-sidebar",
    data() {
        return {
            theStyle: "width:100%;"
        }
    }
}
</script>

<style>
#custom-sidebar {
    width: 100%;
}
</style>