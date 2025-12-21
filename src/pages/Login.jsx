import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ email: "", password: "" });

  async function handleSubmit(e) {
    e.preventDefault();
    await login(form.email, form.password);
    navigate("/"); // go to home or dashboard
  }

  return (
    <div className="login-page">
      <h2>Connexion</h2>
      <form onSubmit={handleSubmit} aria-label="Formulaire de connexion">
        <div className="mb-3">
          <label htmlFor="login-email" className="block text-sm font-medium">Email</label>
          <input
            id="login-email"
            name="email"
            type="email"
            placeholder="Email"
            required
            className="border p-2 rounded w-full"
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
        </div>

        <div className="mb-3">
          <label htmlFor="login-password" className="block text-sm font-medium">Mot de passe</label>
          <input
            id="login-password"
            name="password"
            type="password"
            placeholder="Mot de passe"
            required
            className="border p-2 rounded w-full"
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
        </div>

        <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded">Se connecter</button>
      </form>
    </div>
  );
}
