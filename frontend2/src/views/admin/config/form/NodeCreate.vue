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
          <v-text-field v-model="nodeName" :rules="nameRules" :counter="256" label="Node Name" required></v-text-field>
        </v-col>
      </v-row>
      <v-row v-if="!network">
        <v-col>
          <v-combobox
            v-model="nodeTypeText"
            :items="nodeTypes"
            label="Node Type"
            :rules="typeRules"
            :counter="64"
            required
          ></v-combobox>
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
import { INodeCreate } from '@/interfaces';
import { dispatchCreateNode, dispatchGetNetworks, dispatchGetOneNode } from '@/store/admin/actions';
import { readActiveNode } from '@/store/admin/getters';
import { dispatchGetNodeTypes } from '@/store/utils/actions';
import { readNodeTypes } from '@/store/utils/getters';

@Component
export default class NodeCreate extends Vue {
  // Needed to set the correct type in order to make form functions available
  $refs!: {
    form: HTMLFormElement;
  };

  public valid = false;
  public nodeName = '';
  public nameRules = [
    (v: string | undefined) => !!v || 'Node Name is required',
    (v: string | undefined) => (v && v.length <= 256) || 'Node Name must be less than 256 characters',
  ];

  public nodeTypeText = '';
  public typeRules = [
    (v: string | undefined) => !!v || 'Node Type is required',
    (v: string | undefined) => (v && v.length <= 64) || 'Node Type must be less than 64 characters',
  ];

  get title() {
    if (this.parentNode) {
      return `Add child Node to ${this.parentNode.name}`;
    }
    return 'Create new network.';
  }

  get network() {
    return this.parentNode == null;
  }

  get nodeTypes() {
    return readNodeTypes(this.$store).sort();
  }

  get parentNode() {
    if (this.$route.params.id) {
      return readActiveNode(this.$store);
    }
    return null;
  }

  public async mounted() {
    await dispatchGetNodeTypes(this.$store);
    if (this.$route.params.id) {
      await dispatchGetOneNode(this.$store, parseInt(this.$route.params.id));
    }
    this.reset();
  }

  public close() {
    this.$router.push('/admin/configure');
  }

  public reset() {
    this.$refs.form.reset();
    this.nodeName = '';
    this.nodeTypeText = '';

    // If no parent is given, node type == 'network'
    if (this.parentNode == null) {
      this.nodeTypeText = 'network';
    }
  }

  public async submit() {
    if (await this.$refs.form.validate()) {
      const nodeCreate: INodeCreate = {
        name: this.nodeName,
        node_type: this.nodeTypeText,
      };
      if (this.$route.params.id) {
        nodeCreate.parent_id = parseInt(this.$route.params.id);
      }
      await dispatchCreateNode(this.$store, nodeCreate);
      await dispatchGetNetworks(this.$store);
      this.close();
    }
  }
}
</script>
