<template>
  <v-app id="login" class="primary">
    <v-content>
      <v-container fluid fill-height>
        <v-layout align-center justify-center>
          <v-flex xs12 sm8 md4 lg4>
            <v-card class="elevation-1 pa-3">
              <v-card-text>
                <div class="layout column align-center">
                  <img src="/static/m.png" alt="Vue Material Admin" width="120" height="120">
                  <h1 class="flex my-4 primary--text">用户登陆</h1>
                  <div style="color: red;">{{ message }}</div>
                </div>                
                <v-form>
                  <v-text-field append-icon="person" name="login" label="Login" type="text" v-model="model.username"></v-text-field>
                  <v-text-field append-icon="lock" name="password" label="Password" id="password" type="password" v-model="model.password"></v-text-field>
                </v-form>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn block color="primary" @click="login" :loading="loading">Login</v-btn>
              </v-card-actions>
            </v-card>
          </v-flex>
        </v-layout>
      </v-container>
    </v-content>
  </v-app>
</template>

<script>
import md5 from 'js-md5';

export default {
  data: () => ({
    loading: false,
    model: {
      username: '',
      password: ''
    },
    message: '',
  }),

  methods: {
    login () {
      this.loading = true;
      this.message = '';
      this.axios.post('/api/admin/login', 'username=' + this.model.username + '&password=' + md5(this.model.password)).then((response) => {
        if (response.data.state !== 1) {
          this.loading = false;
          this.message = response.data.message;
        } else {
          this.$router.push('/');
        }
      });
    }
  }

};
</script>
<style scoped lang="css">
  #login {
    height: 50%;
    width: 100%;
    position: absolute;
    top: 0;
    left: 0;
    content: "";
    z-index: 0;
  }
</style>
