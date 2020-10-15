<template>
  <v-form v-model="valid" ref="form" lazy-validation>
    <v-container class="pa-3">
      <v-row>
        <v-col v-if="!network">
          <h2>{{ node ? `Update Node: ${node.name}` : 'Update Node' }}</h2>
        </v-col>
        <v-col v-else>
          <h2>{{ node ? `Update Network: ${node.name}` : 'Update Network' }}</h2>
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
        <v-col>
          <v-switch v-model="isActive" inset label="Is Node Active?"></v-switch>
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
import { INode, INodeUpdate } from '@/interfaces';
import { dispatchGetOneNode, dispatchUpdateNode } from '@/store/admin/actions';
import { readActiveNode } from '@/store/admin/getters';
import { dispatchGetNodeTypes } from '@/store/utils/actions';
import { readNodeTypes } from '@/store/utils/getters';

@Component
export default class NodeEditForm extends Vue {
  @Prop(Number) readonly id: number | undefined;

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

  public isActive = false;

  public get node(): INode | null {
    return readActiveNode(this.$store);
  }

  get nodeTypes() {
    return readNodeTypes(this.$store).sort();
  }

  get network() {
    if (this.node) {
      return this.node.parent_id == null;
    }
    return false;
  }

  @Watch('id')
  public async refresh(val: number) {
    await dispatchGetNodeTypes(this.$store);
    await dispatchGetOneNode(this.$store, val);
    this.reset();
  }

  public async mounted() {
    await dispatchGetNodeTypes(this.$store);
    if (this.id) {
      await dispatchGetOneNode(this.$store, this.id);
    }
    this.reset();
  }

  public reset() {
    if (this.node) {
      this.nodeName = this.node.name;
      this.nodeTypeText = this.node.node_type;
      this.isActive = this.node.is_active;
    }
  }

  public async submit() {
    if ((await this.$refs.form.validate()) && this.id && this.node) {
      const nodeUpdate: INodeUpdate = {
        name: this.nodeName,
        node_type: this.nodeTypeText,
        is_active: this.isActive,
      };
      await dispatchUpdateNode(this.$store, { id: this.id, object: nodeUpdate });
      this.cancel();
    }
  }

  @Emit('input')
  public cancel() {
    return false;
  }
}
</script>
