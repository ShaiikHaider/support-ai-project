import { useState, useEffect } from 'react';

const phrases = [
  "actually resolves issues",
  "escalates only when needed",
  "never sleeps",
  "understands context"
];

const headlineWords = "The support console that".split(" ");

export function HeroVisual() {
  const [index, setIndex] = useState(0);
  const [fade, setFade] = useState(true);

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
    <div className="hidden lg:flex lg:flex-1 relative bg-[#09090b] overflow-hidden flex-col justify-between p-12">
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-accent-500 rounded-full blur-[200px] opacity-[0.07] pointer-events-none translate-x-1/3 -translate-y-1/3"></div>

      <div className="relative z-10 flex items-center h-full">
        <div className="max-w-lg">
          <div className="flex items-center gap-2 mb-8 opacity-0 animate-fade-in-up" style={{ animationDelay: '100ms' }}>
            <div className="w-8 h-8 rounded-lg bg-[#18181b] border border-[#27272a] flex items-center justify-center">
              {/* Customer service headset icon instead of AI lightning bolt */}
              <svg className="w-4 h-4 text-slate-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M18 11V9a6 6 0 00-12 0v2M18 11c1.104 0 2 .896 2 2v1c0 1.104-.896 2-2 2h-2c-1.104 0-2-.896-2-2v-3c0-1.104.896-2 2-2h2zm-12 0c-1.104 0-2 .896-2 2v1c0 1.104.896 2 2 2h2c1.104 0 2-.896 2-2v-3c0-1.104-.896-2-2-2H6z" />
              </svg>
            </div>
            <span className="text-sm font-semibold tracking-widest text-slate-400 uppercase">Resolve</span>
          </div>

          <h2 className="text-5xl font-semibold text-white tracking-tight leading-[1.1]">
            {headlineWords.map((word, i) => (
              <span 
                key={i} 
                className="inline-block opacity-0 animate-fade-in-up mr-2"
                style={{ animationDelay: `${200 + i * 100}ms` }}
              >
                {word}
              </span>
            ))}
            <br />
            <span 
              className={`inline-block transition-all duration-400 ease-out text-slate-400 opacity-0 animate-fade-in-up ${
                fade ? 'opacity-100 translate-y-0 blur-none' : 'opacity-0 translate-y-2 blur-[2px]'
              }`}
              style={{ animationDelay: `${200 + headlineWords.length * 100 + 100}ms` }}
            >
              {phrases[index]}.
            </span>
          </h2>
          <p className="mt-8 text-lg text-slate-400 leading-relaxed max-w-md opacity-0 animate-fade-in-up" style={{ animationDelay: '800ms' }}>
            Empower your team with agentic workflows. Automate the repetitive, intelligently route the complex, and deliver faster resolutions.
          </p>
        </div>
      </div>

      <div className="relative z-10 flex items-center justify-between text-sm text-slate-500 font-medium opacity-0 animate-fade-in-up" style={{ animationDelay: '1000ms' }}>
        <span>© 2026 Resolve Inc.</span>
        <span>Enterprise ready</span>
      </div>
    </div>
  );
}
