import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { HeroVisual } from "../components/HeroVisual";

export function RegisterPage() {
  const { signUp } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await signUp(email, fullName, password);
      navigate("/login");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Could not create account.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex min-h-screen bg-slate-50 dark:bg-panel-900">
      <div className="flex flex-1 flex-col justify-center px-4 py-12 sm:px-6 lg:flex-none lg:px-20 xl:px-24 w-full lg:w-1/2 relative z-10">
        <div className="mx-auto w-full max-w-sm lg:w-96">
          <div>
            <h2 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-slate-100">
              Create your account
            </h2>
            <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
              Get support from the agentic resolution system.
            </p>
          </div>

          <div className="mt-8">
            <form onSubmit={handleSubmit} className="space-y-5">
              <Field label="Full name" type="text" value={fullName} onChange={setFullName} />
              <Field label="Email address" type="email" value={email} onChange={setEmail} />
              <Field label="Password" type="password" value={password} onChange={setPassword} />

              {error && <p className="text-sm text-red-500 font-medium">{error}</p>}

              <button
                type="submit"
                disabled={loading}
                className="flex w-full justify-center rounded-xl bg-accent-600 px-3 py-3 text-sm font-semibold text-white shadow-sm hover:bg-accent-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-accent-600 transition-colors disabled:opacity-50"
              >
                {loading ? "Creating account..." : "Create account"}
              </button>
            </form>

            <p className="mt-10 text-center text-sm text-slate-600 dark:text-slate-400">
              Already have an account?{" "}
              <Link to="/login" className="font-semibold leading-6 text-accent-600 hover:text-accent-500">
                Sign in here
              </Link>
            </p>
          </div>
        </div>
      </div>
      
      <HeroVisual />
    </div>
  );
}

function Field({ label, type, value, onChange }: { label: string; type: string; value: string; onChange: (v: string) => void; }) {
  return (
    <div>
      <label className="block text-sm font-medium leading-6 text-slate-900 dark:text-slate-200">
        {label}
      </label>
      <div className="mt-2">
        <input
          type={type}
          required
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="block w-full rounded-xl border-0 py-3 text-slate-900 dark:text-slate-100 bg-white dark:bg-panel-800 shadow-sm ring-1 ring-inset ring-slate-300 dark:ring-panel-700 placeholder:text-slate-400 focus:ring-2 focus:ring-inset focus:ring-accent-600 sm:text-sm sm:leading-6 transition-all"
        />
      </div>
    </div>
  );
}
