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
          <v-text-field
            v-model="userGroupName"
            :rules="nameRules"
            :counter="256"
            label="User Group Name"
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
import { dispatchGetOneNode, dispatchCreateUserGroup, dispatchGetNetworks } from '@/store/admin/actions';
import { readActiveNode } from '@/store/admin/getters';
import { IUserGroupCreate } from '@/interfaces';

@Component
export default class ConfigureUserGroupForm extends Vue {
  // Needed to set the correct type in order to make form functions available
  $refs!: {
    form: HTMLFormElement;
  };

  public valid = false;
  public userGroupName = '';
  public nameRules = [
    (v: string | undefined) => !!v || 'User Group Name is required',
    (v: string | undefined) => (v && v.length <= 256) || 'User Group Name must be less than 256 characters',
  ];

  get title() {
    if (this.activeNode) {
      return `Add User Group to ${this.activeNode.name}`;
    }
    return 'Add User Group to Node';
  }

  get activeNode() {
    return readActiveNode(this.$store);
  }

  public async mounted() {
    await dispatchGetOneNode(this.$store, parseInt(this.$route.params.id));
  }

  public close() {
    this.$router.push('/admin/configure');
  }

  public reset() {
    this.$refs.form.reset();
    this.userGroupName = '';
  }

  public async submit() {
    if (await this.$refs.form.validate()) {
      const userGroupCreate: IUserGroupCreate = {
        name: this.userGroupName,
        node_id: parseInt(this.$route.params.id),
      };
      await dispatchCreateUserGroup(this.$store, userGroupCreate);
    }
    await dispatchGetNetworks(this.$store);
    this.close();
  }
}
</script>
