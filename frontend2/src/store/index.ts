import Vue from 'vue';
import Vuex, { StoreOptions } from 'vuex';

import { mainModule } from './main';
import { adminModule } from './admin';
import { interfaceModule } from './interfaces';
import { utilsModule } from './utils';
import { State } from './state';

Vue.use(Vuex);

const storeOptions: StoreOptions<State> = {
  modules: {
    main: mainModule,
    admin: adminModule,
    interfaces: interfaceModule,
    utils: utilsModule,
  },
};

export const store = new Vuex.Store<State>(storeOptions);

export default store;
