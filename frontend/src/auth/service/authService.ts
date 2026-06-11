import { apiClient } from "../../travel/service/apiClient";

export type AuthUser = { id: number; username: string; name: string };

export type RegisterInput = {
  username: string;
  password: string;
  first_name?: string;
  last_name?: string;
};

export async function register(input: RegisterInput): Promise<AuthUser> {
  const { data } = await apiClient.post<AuthUser>("/api/auth/register/", input);
  return data;
}

export async function login(username: string, password: string): Promise<AuthUser> {
  const { data } = await apiClient.post<AuthUser>("/api/auth/login/", { username, password });
  return data;
}

export async function logout(): Promise<void> {
  await apiClient.post("/api/auth/logout/");
}

export async function me(): Promise<AuthUser | null> {
  const { data } = await apiClient.get<AuthUser | null>("/api/auth/me/");
  return data ?? null;
}
