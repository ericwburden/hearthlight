<template>
  <v-form v-model="valid" ref="form" lazy-validation>
    <v-container>
      <v-row>
        <v-col cols="10">
          <h2>{{ title }}</h2>
        </v-col>
        <v-col class="d-flex justify-end" cols="2">
          <v-btn icon color="error" @click="close()" large><v-icon>mdi-close-circle</v-icon></v-btn>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-text-field v-model="fullName" :rules="nameRules" :counter="256" label="Full Name" required></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-text-field
            v-model="userEmail"
            :rules="emailRules"
            :counter="256"
            label="Email Address"
            required
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-text-field
            v-model="password"
            :rules="passwordRules"
            :counter="256"
            label="Password"
            required
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col class="d-flex justify-end">
          <v-btn color="warning" @click="reset" class="mx-2">Reset</v-btn>
          <v-btn color="success" @click="submit" class="mx-2">Submit</v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>

<script lang="ts">
/* eslint-disable @typescript-eslint/camelcase */
import { Component, Vue } from 'vue-property-decorator';
import { IUserProfileCreate } from '@/interfaces';
import { dispatchCreateUser, dispatchGetNetworks, dispatchGetOneUserGroup } from '@/store/admin/actions';
import { readActiveUserGroup } from '@/store/admin/getters';

@Component
export default class UserCreate extends Vue {
  // Needed to set the correct type in order to make form functions available
  $refs!: {
    form: HTMLFormElement;
  };

  emailRegex = new RegExp(
    // eslint-disable-next-line no-useless-escape
    /^(([^<>()\[\]\\.,;:\s@"]+(\.[^<>()\[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/,
  );
  passwordRegex = new RegExp(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/);

  public valid = false;
  public userEmail = '';
  public emailRules = [
    (v: string | undefined) => !!v || 'Email address is required',
    (v: string | undefined) => (v && this.emailRegex.test(v)) || 'Email address must be a valid email address',
    (v: string | undefined) => (v && v.length <= 256) || 'Email address must be less than 256 characters',
  ];

  public fullName = '';
  public nameRules = [
    (v: string | undefined) => !!v || 'Full Name is required',
    (v: string | undefined) => (v && v.length <= 256) || 'Full Name must be less than 256 characters',
  ];

  public password = '';
  public passwordRules = [
    (v: string | undefined) => !!v || 'Password is required',
    (v: string | undefined) =>
      (v && this.passwordRegex.test(v)) ||
      'Password must contain at least 8 characters, including one uppercase letter, one lowercase letter, one number, and one special character (@$!%*?&)',
    (v: string | undefined) => (v && v.length <= 256) || 'Password must be less than 256 characters',
  ];

  public async mounted() {
    if (this.$route.params.id) {
      await dispatchGetOneUserGroup(this.$store, parseInt(this.$route.params.id));
    }
    this.reset();
  }

  get userGroup() {
    if (this.$route.params.id) {
      return readActiveUserGroup(this.$store);
    }
    return null;
  }

  get title() {
    if (this.userGroup) {
      return `Add user to ${this.userGroup.name}`;
    }
    return `Add new user`;
  }

  public close() {
    this.$router.push('/admin/configure');
  }

  public reset() {
    this.$refs.form.reset();
    this.userEmail = '';
    this.fullName = '';
    this.password = '';
  }

  public async submit() {
    if (await this.$refs.form.validate()) {
      const userCreate: IUserProfileCreate = {
        email: this.userEmail,
        full_name: this.fullName,
        password: this.password,
        user_group_id: parseInt(this.$route.params.id),
      };
      await dispatchCreateUser(this.$store, userCreate);
      await dispatchGetNetworks(this.$store);
      this.close();
    }
  }
}
</script>
