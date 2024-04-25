<template>
    <div class="container-fluid vh-100 d-flex justify-content-center align-items-center bg-dark">
        <b-card variant="dark" header="Smart Intrusion Detection" header-tag="h1"
            class="text-center w-50 shadow rounded-lg">
            <div style="max-width: 50%;display:block;margin-left:auto;margin-right:auto;">
                <b-form @submit.prevent="handleSubmit">
                    <b-form-group label="Username">
                        <b-form-input style="background-color: rgba(0,0,0,0);" type="text" v-model="username"
                            placeholder="Enter username" required />
                    </b-form-group>
                    <b-form-group label="Password">
                        <b-form-input style="background-color: rgba(0,0,0,0);" type="password" v-model="password"
                            placeholder="Enter password" required />
                    </b-form-group>
                    <p style="color:red;">Invalid Authentication</p>
                    <!-- <b-form-checkbox v-model="rememberMe">Remember Me</b-form-checkbox> -->
                    <button type="submit" variant="primary" class="btn btn-outline-primary">Login</button>

                </b-form>
            </div>
        </b-card>
    </div>
</template>


<script>
export default {
    data() {
        return {
            username: "",
            password: "",
            rememberMe: false,
        };
    },
    methods: {
        handleSubmit() {
            // Simulate login logic (replace with your API call)
            const formData = new FormData();
            formData.append("username", this.username);
            formData.append("password", this.password);
            fetch('http://localhost:8001/intrusion-detection/login/', {
                method: 'POST',
                body: formData,
                // headers: headers,
            })
                .then(response => response.json())
                .then(data => {
                    let token = data['token']
                    if (!token) {

                    } else {
                        localStorage.setItem("token", token);
                        localStorage.setItem("username", this.username);
                        this.$router.push("/"); // Redirect to home page
                    }

                })
                .catch(error => {
                    console.error('Error:', error);
                });
        },

    },
    mounted() {
        document.title = "Login";
    }
};
</script>


<style>
/* Customize the login card appearance (optional) */
.b-card-header {
    color: #fff;
    font-weight: bold;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.b-card {
    border: none;
    background-color: rgba(0, 0, 0, 0.7);

}

.shadow {
    box-shadow: 0 0 10px rgba(0, 0, 0, 0.3);
}

.rounded-lg {
    border-radius: 1rem;
}

.input {
    color: rgba(0, 0, 0, 0);
}
</style>