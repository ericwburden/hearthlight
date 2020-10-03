<template>
  <v-form v-model="valid" ref="nodeCreateForm" lazy-validation>
    <v-container v-if="deleteForm">
      <v-row>
        <v-col>
          <h2>Really delete node {{ name }}?</h2>
        </v-col>
      </v-row>
      <v-row>
        <v-col>
          <v-btn x-large color="warning" @click="close">Cancel</v-btn>
        </v-col>
        <v-col>
          <v-btn x-large color="error" @click="confirm">Delete</v-btn>
        </v-col>
      </v-row>
    </v-container>
    <v-container v-else>
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
      <v-row class="d-none">
        <v-col>
          <v-text-field v-model="nodeParentId" :rules="numberRules" label="Parent ID" type="number"></v-text-field>
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
import { Component, Vue, Watch } from 'vue-property-decorator';
import { INodeCreate, INodeUpdate } from '@/interfaces';
import {
  dispatchCreateNode,
  dispatchDeleteNode,
  dispatchGetNetworks,
  dispatchGetNodeTypes,
  dispatchGetOneNode,
  dispatchUpdateNode,
} from '@/store/admin/actions';
import { readActiveNode, readConfigureNodeFormProps, readNodeTypes } from '@/store/admin/getters';

@Component
export default class CreateNodeForm extends Vue {
  // Needed to set the correct type in order to make form functions available
  $refs!: {
    nodeCreateForm: HTMLFormElement;
  };

  public title = this.props.title;
  public network = this.props.network;
  public deleteForm = this.props.delete;
  public name = this.activeNode ? this.activeNode.name : null;
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

  public nodeParentId: string | null = null;
  public numberRules = [
    (v: string | undefined) => (v && !isNaN(+v)) || v == null || 'Node Parent ID must be a number if given',
  ];

  get nodeTypes() {
    return readNodeTypes(this.$store).sort();
  }

  get activeNode() {
    return readActiveNode(this.$store);
  }

  get props() {
    return readConfigureNodeFormProps(this.$store);
  }

  @Watch('parentID')
  onIdChange() {
    this.reset();
  }

  public async mounted() {
    await dispatchGetNodeTypes(this.$store);
    if (this.props.id) {
      await dispatchGetOneNode(this.$store, this.props.id);
    }
    this.reset();
  }

  public close() {
    this.$router.push('/admin/configure');
  }

  public reset() {
    this.$refs.nodeCreateForm.reset();
    if (this.props.id && this.activeNode) {
      // If the 'id' prop is set, populate the fields
      this.nodeName = this.activeNode.name;
      this.nodeTypeText = this.activeNode.node_type;
      if (this.activeNode.parent_id) {
        this.nodeParentId = this.activeNode.parent_id.toString();
      }
    } else {
      // Empty fields if the 'id' prop is missing
      this.nodeName = '';
      this.nodeTypeText = '';
      this.nodeParentId = null;

      // If the parentID prop is set, set nodeParentId
      if (this.props.parent) {
        this.nodeParentId = this.props.parent.toString();
      }

      // If the network prop is set, set node_type to 'network'
      if (this.props.network) {
        this.nodeTypeText = 'network';
      }
    }
  }

  public async submit() {
    if (await this.$refs.nodeCreateForm.validate()) {
      if (this.props.id) {
        // If the 'id' prop is set, update the node
        const nodeUpdate: INodeUpdate = {
          name: this.nodeName,
          node_type: this.nodeTypeText,
        };
        if (this.activeNode && this.activeNode.parent_id) {
          nodeUpdate.parent_id = this.activeNode.parent_id;
        }
        await dispatchUpdateNode(this.$store, [this.props.id, nodeUpdate]);
      } else {
        // Create a new node if the 'id' prop is missing
        const nodeCreate: INodeCreate = {
          name: this.nodeName,
          node_type: this.nodeTypeText,
        };
        if (this.props.parent) {
          nodeCreate.parent_id = this.props.parent;
        }
        await dispatchCreateNode(this.$store, nodeCreate);
      }

      await dispatchGetNetworks(this.$store);
      this.close();
    }
  }

  public async confirm() {
    if (this.props.id) {
      await dispatchDeleteNode(this.$store, this.props.id);
    }
    await dispatchGetNetworks(this.$store);
    this.close();
  }
}
</script>
