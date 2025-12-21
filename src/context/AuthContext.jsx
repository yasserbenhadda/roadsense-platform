import { createContext, useState, useContext } from "react";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [accessToken, setAccessToken] = useState(null);

  async function login(email, password) {
    const res = await fetch("/auth/login", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      credentials: "include",  // <- important for refresh cookie
      body: JSON.stringify({ email, password })
    });

    const data = await res.json();

    setUser(data.user);
    setAccessToken(data.accessToken);
  }

  async function refreshToken() {
    const res = await fetch("/auth/refresh", {
      method: "POST",
      credentials: "include"
    });
    const data = await res.json();
    setAccessToken(data.accessToken);
  }

  function logout() {
    setUser(null);
    setAccessToken(null);
    fetch("/auth/logout", { method: "POST", credentials: "include" });
  }

  return (
    <AuthContext.Provider value={{ user, accessToken, login, logout, refreshToken }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
