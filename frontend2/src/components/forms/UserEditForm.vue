<template>
  <v-form v-model="valid" ref="form" lazy-validation>
    <v-container class="pa-3">
      <v-row>
        <v-col>
          <h2>{{ user ? `Update User: ${user.email}` : 'Update User' }}</h2>
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
          <v-switch v-if="isUserActive" v-model="isUserActive" label="Active User"></v-switch>
        </v-col>
        <v-col>
          <v-switch v-model="isSuperUser" label="Superuser"></v-switch>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-text-field
            v-model="password"
            :rules="passwordRules"
            :counter="256"
            label="New Password"
            type="password"
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-text-field
            v-model="passwordConfirm"
            :error-messages="passwordConfirmErrors"
            :counter="256"
            label="Confirm New Password"
            type="password"
          ></v-text-field>
        </v-col>
      </v-row>
      <v-row>
        <v-spacer></v-spacer>
        <v-col class="px-0 flex-grow-0">
          <v-btn color="warning" @click="cancel" class="mx-2">Cancel</v-btn>
        </v-col>
        <v-col class="px-0 flex-grow-0">
          <v-btn color="secondary" @click="reset" class="mx-2">Reset</v-btn>
        </v-col>
        <v-col class="px-0 flex-grow-0">
          <v-btn color="success" @click="submit" class="mx-2">Submit</v-btn>
        </v-col>
      </v-row>
    </v-container>
  </v-form>
</template>

<script lang="ts">
/* eslint-disable @typescript-eslint/camelcase */
import { Component, Emit, Prop, Vue, Watch } from 'vue-property-decorator';
import { IUserProfile, IUserProfileUpdate } from '@/interfaces';
import { dispatchGetOneUser, dispatchUpdateUser } from '@/store/admin/actions';
import { readActiveUser } from '@/store/admin/getters';

@Component
export default class UserEditForm extends Vue {
  @Prop(Number) readonly id: number | undefined;

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
    (v: string | undefined) => !v || (v && v.length <= 256) || 'Full Name must be less than 256 characters',
  ];

  public isUserActive = false;
  public isSuperUser = false;

  public password = '';
  public passwordConfirm = '';
  public passwordConfirmError = false;
  public passwordConfirmErrors: string[] = [];
  public passwordRules = [
    (v: string | undefined) =>
      !v ||
      (v && this.passwordRegex.test(v)) ||
      'Password must contain at least 8 characters, including one uppercase letter, one lowercase letter, one number, and one special character (@$!%*?&)',
    (v: string | undefined) => !v || (v && v.length <= 256) || 'Password must be less than 256 characters',
  ];

  public get user(): IUserProfile | null {
    return readActiveUser(this.$store);
  }

  @Watch('id')
  public async refresh(val: number) {
    await dispatchGetOneUser(this.$store, val);
    this.reset();
  }

  public async mounted() {
    if (this.id) {
      await dispatchGetOneUser(this.$store, this.id);
    }
    this.reset();
  }

  public reset() {
    if (this.user) {
      this.userEmail = this.user.email;
      this.fullName = this.user.full_name;
      this.isUserActive = this.user.is_active;
      this.isSuperUser = this.user.is_superuser;
      this.password = '';
      this.passwordConfirm = '';
      this.passwordConfirmError = false;
      this.passwordConfirmErrors = [];
    }
  }

  public async submit() {
    if ((await this.$refs.form.validate()) && this.id && this.user) {
      const userUpdate: IUserProfileUpdate = {
        full_name: this.fullName,
        is_active: this.isUserActive,
        is_superuser: this.isSuperUser,
      };
      if (this.password) {
        if (this.password === this.passwordConfirm) {
          this.passwordConfirmError = false;
          this.passwordConfirmErrors = [];
          userUpdate.password = this.password;
        } else {
          this.passwordConfirmError = true;
          this.passwordConfirmErrors = ['Password must match confirmation'];
        }
      }
      if (this.userEmail != this.user.email) {
        userUpdate.email = this.userEmail;
      }
      await dispatchUpdateUser(this.$store, { id: this.id, object: userUpdate });
      this.cancel();
    }
  }

  @Emit('input')
  public cancel() {
    return false;
  }
}
</script>
