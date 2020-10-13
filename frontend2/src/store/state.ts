import { MainState } from './main/state';
import { AdminState } from './admin/state';
import { InterfaceState } from './interfaces/state';

export interface State {
  main: MainState;
  admin: AdminState;
  interfaces: InterfaceState;
}
