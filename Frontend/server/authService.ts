// src/services/authService.ts

export type RegistrationPayload = {
  firstName: string;
  lastName: string;
  email: string;
  country: string;
  password: string;
  market: string;
  strategies: string[];
};

export async function registerUser(payload: RegistrationPayload) {
  // 🔁 BACKEND API URL (to be replaced later)
  const API_URL = "https://api.yourdomain.com/register";

  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error("Registration failed");
    }

    return await response.json();
  } catch (error) {
    console.error("Register API error:", error);
    throw error;
  }
}
