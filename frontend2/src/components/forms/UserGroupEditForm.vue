<template>
  <v-form v-model="valid" ref="form" lazy-validation>
    <v-container class="pa-3">
      <v-row>
        <v-col>
          <h2>{{ userGroup ? `Update User Group: ${userGroup.name}` : 'Update User Group' }}</h2>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-text-field v-model="name" :rules="nameRules" :counter="256" label="Name" required></v-text-field>
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
import { IUserGroup, IUserGroupUpdate } from '@/interfaces';
import { dispatchGetOneUser, dispatchGetOneUserGroup, dispatchUpdateUserGroup } from '@/store/admin/actions';
import { readActiveUserGroup } from '@/store/admin/getters';

@Component
export default class UserGroupEditForm extends Vue {
  @Prop(Number) readonly id: number | undefined;

  // Needed to set the correct type in order to make form functions available
  $refs!: {
    form: HTMLFormElement;
  };

  public valid = false;
  public name = '';
  public nameRules = [
    (v: string | undefined) => !!v || 'Node Name is required',
    (v: string | undefined) => (v && v.length <= 256) || 'Node Name must be less than 256 characters',
  ];

  public get userGroup(): IUserGroup | null {
    return readActiveUserGroup(this.$store);
  }

  @Watch('id')
  public async refresh(val: number) {
    await dispatchGetOneUserGroup(this.$store, val);
    this.reset();
  }

  public async mounted() {
    if (this.id) {
      await dispatchGetOneUserGroup(this.$store, this.id);
    }
    this.reset();
  }

  public reset() {
    if (this.userGroup) {
      this.name = this.userGroup.name;
    }
  }

  public async submit() {
    if ((await this.$refs.form.validate()) && this.id && this.userGroup) {
      const userGroupUpdate: IUserGroupUpdate = {
        name: this.name,
      };
      await dispatchUpdateUserGroup(this.$store, { id: this.id, object: userGroupUpdate });
      this.cancel();
    }
  }

  @Emit('input')
  public cancel() {
    return false;
  }
}
</script>
