import { useState, useEffect } from "react";
import { Link } from "react-router-dom";

const phrases = [
  "actually resolves issues",
  "escalates only when needed",
  "never sleeps",
  "understands context"
];

const headlineWords = "AI-powered customer support that".split(" ");

export function LandingPage() {
  const [index, setIndex] = useState(0);
  const [fade, setFade] = useState<boolean>(true);
  const [isDarkMode, setIsDarkMode] = useState<boolean>(true);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [isDarkMode]);

  useEffect(() => {
    const interval = setInterval(() => {
      setFade(false); 
      setTimeout(() => {
        setIndex((prev) => (prev + 1) % phrases.length);
        setFade(true); 
      }, 400); 
    }, 3500); 
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="flex min-h-[100dvh] flex-col bg-slate-50 dark:bg-[#09090b] transition-colors duration-300">
      {/* Header */}
      <header className="absolute inset-x-0 top-0 z-50 flex h-16 items-center justify-between px-6 lg:px-12 bg-white/50 dark:bg-[#09090b]/50 backdrop-blur-md border-b border-slate-200 dark:border-[#27272a]">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-slate-900 dark:bg-[#18181b] border border-slate-700 dark:border-[#27272a] flex items-center justify-center">
            {/* Customer service headset icon instead of AI lightning bolt */}
            <svg className="w-4 h-4 text-slate-100 dark:text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 11V9a6 6 0 00-12 0v2M18 11c1.104 0 2 .896 2 2v1c0 1.104-.896 2-2 2h-2c-1.104 0-2-.896-2-2v-3c0-1.104.896-2 2-2h2zm-12 0c-1.104 0-2 .896-2 2v1c0 1.104.896 2 2 2h2c1.104 0 2-.896 2-2v-3c0-1.104-.896-2-2-2H6z" />
            </svg>
          </div>
          <span className="text-sm font-bold tracking-widest text-slate-900 dark:text-slate-300 uppercase">Resolve</span>
        </div>
        
        <div className="flex items-center gap-4">
          <button
            onClick={() => setIsDarkMode(!isDarkMode)}
            className="flex items-center justify-center w-9 h-9 rounded-full bg-slate-200 hover:bg-slate-300 dark:bg-panel-800 dark:hover:bg-panel-700 text-slate-600 dark:text-slate-300 transition-colors focus:outline-none focus:ring-2 focus:ring-accent-500/50"
            title="Toggle theme"
          >
            {isDarkMode ? (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
            ) : (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" /></svg>
            )}
          </button>

          <div className="h-5 w-px bg-slate-300 dark:bg-panel-700 mx-1"></div>

          <Link to="/login" className="text-sm font-medium text-slate-700 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors">
            Log in
          </Link>
          <Link to="/register" className="text-sm font-semibold text-white bg-accent-600 hover:bg-accent-500 px-4 py-2 rounded-lg transition-colors shadow-sm">
            Sign up
          </Link>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex flex-col justify-center relative overflow-hidden">
        {/* Subtle accent glow */}
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] md:w-[800px] md:h-[800px] bg-accent-500 rounded-full blur-[250px] opacity-[0.08] pointer-events-none"></div>
        
        <div className="relative z-10 mx-auto max-w-5xl px-6 text-center mt-16">
          <h1 className="text-5xl md:text-7xl font-semibold text-slate-900 dark:text-white tracking-tight leading-[1.15]">
            {headlineWords.map((word, i) => (
              <span 
                key={i} 
                className="inline-block opacity-0 animate-fade-in-up mr-3"
                style={{ animationDelay: `${200 + i * 80}ms` }}
              >
                {word}
              </span>
            ))}
            <br className="hidden md:block" />
            <span 
              className={`inline-block transition-all duration-400 ease-out text-accent-600 dark:text-slate-400 opacity-0 animate-fade-in-up mt-2 md:mt-4 ${
                fade ? 'opacity-100 translate-y-0 blur-none' : 'opacity-0 translate-y-2 blur-[2px]'
              }`}
              style={{ animationDelay: `${200 + headlineWords.length * 80 + 100}ms` }}
            >
              {phrases[index]}.
            </span>
          </h1>
          <p className="mt-8 text-lg md:text-xl text-slate-600 dark:text-slate-400 leading-relaxed max-w-2xl mx-auto opacity-0 animate-fade-in-up" style={{ animationDelay: '900ms' }}>
            Empower your team with agentic workflows. Automate the repetitive, intelligently route the complex, and deliver faster resolutions without the wait.
          </p>
          <div className="mt-12 flex flex-col sm:flex-row items-center justify-center gap-4 opacity-0 animate-fade-in-up" style={{ animationDelay: '1100ms' }}>
            <Link to="/register" className="w-full sm:w-auto text-base font-semibold text-white bg-accent-600 hover:bg-accent-500 px-8 py-4 rounded-xl transition-all shadow-sm hover:shadow-md focus:ring-4 focus:ring-accent-500/20">
              Get started for free
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
