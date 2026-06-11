import { useState } from "react";
import { FormField } from "../../../components/FormField/FormField";
import { useAuth } from "../../AuthContext";
import "./LoginPage.css";

type Mode = "login" | "register";

function extractError(err: unknown): string {
  const anyErr = err as { response?: { data?: Record<string, unknown> } };
  const data = anyErr?.response?.data;
  if (data) {
    const first = Object.values(data)[0];
    if (Array.isArray(first)) return String(first[0]);
    if (typeof first === "string") return first;
  }
  return "Não foi possível concluir. Tente novamente.";
}

export function LoginPage() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<Mode>("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setSubmitting(true);
    try {
      if (mode === "login") {
        await login(username, password);
      } else {
        const [first_name, ...rest] = name.trim().split(" ");
        await register({
          username,
          password,
          first_name: first_name ?? "",
          last_name: rest.join(" "),
        });
      }
    } catch (err) {
      setError(extractError(err));
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <h1>iziline</h1>
        <p className="subtitle">
          {mode === "login" ? "Entre na sua conta" : "Crie sua conta"}
        </p>
        <form onSubmit={handleSubmit}>
          {mode === "register" && (
            <FormField
              id="name"
              label="Nome"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Seu nome"
            />
          )}
          <FormField
            id="username"
            label="Usuário"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <FormField
            id="password"
            label="Senha"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          {error && <span className="form-error">{error}</span>}
          <button type="submit" className="primary" disabled={submitting}>
            {submitting ? "Aguarde..." : mode === "login" ? "Entrar" : "Criar conta"}
          </button>
        </form>
        <div className="toggle">
          {mode === "login" ? "Não tem conta?" : "Já tem conta?"}{" "}
          <button
            type="button"
            onClick={() => {
              setError("");
              setMode(mode === "login" ? "register" : "login");
            }}
          >
            {mode === "login" ? "Criar conta" : "Entrar"}
          </button>
        </div>
      </div>
    </div>
  );
}
