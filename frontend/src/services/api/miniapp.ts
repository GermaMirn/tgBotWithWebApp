import { api } from "./axios";


export const miniapp = async (id: Number, username: String, full_name: String) => {
  try {
    const response = await api.post("/auth/miniapp", {
      id,
      username,
      full_name
    });
    return response.data;
  } catch (error) {
    alert("Ошибка:"+ error);
    throw error;
  }
};
