import { MainState } from './main/state';
import { AdminState } from './admin/state';

export interface State {
  main: MainState;
  admin: AdminState;
}
