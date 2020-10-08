export interface IUserProfile {
  email: string;
  is_active: boolean;
  is_superuser: boolean;
  full_name: string;
  id: number;
}

export interface IUserProfileList {
  total_records: number;
  records: IUserProfile[];
}

export interface IUserProfileUpdate {
  email?: string;
  full_name?: string;
  password?: string;
  is_active?: boolean;
  is_superuser?: boolean;
}

export interface IUserProfileCreate {
  email: string;
  full_name?: string;
  password?: string;
  is_active?: boolean;
  is_superuser?: boolean;
  user_group_id?: number;
}
