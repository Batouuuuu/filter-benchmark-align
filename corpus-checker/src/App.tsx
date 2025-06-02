import { useEffect } from "react";
import Particles from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import { tsParticles } from "@tsparticles/engine";

export default function App() {
  useEffect(() => {
    async function load() {
      await loadSlim(tsParticles);
    }
    load();
  }, []);

  return (
    <div className="relative h-screen w-screen overflow-hidden ">
      <Particles
        id="tsparticles"
        className="absolute inset-0 pointer-events-none"
        style={{ zIndex: -1 }}
        options={{
          background: { color: "rgba(0,0,0,0.6)" },
          particles: {
            number: { value: 150, density: { enable: true } },
            color: { value: ["#a0ff9e", "#ccff66", "#e0ffb3"] },
            shape: { type: "circle" },
            opacity: {
              value: { min: 0.3, max: 0.7 },
              animation: { enable: true, speed: 0.5, sync: false },
            },
            size: {
              value: { min: 1, max: 4 },
              animation: { enable: true, speed: 1, sync: false },
            },
            move: {
              enable: true,
              speed: 1,
              direction: "none",
              random: true,
              straight: false,
              outModes: { default: "out" },
            },
            wobble: { enable: true, distance: 3, speed: 1 },
            twinkle: {
              particles: { enable: true, frequency: 0.03, opacity: 1 },
            },
            shadow: {
              enable: true,
              color: "#a0ff9e",
              blur: 10,
              offset: { x: 0, y: 0 },
            },
          },
          detectRetina: true,
        }}
      />

      <div className="top-1/2 left-0 right-0 max-w-4xl w-full mx-auto h-[400px] transform -translate-y-1/2 p-6 rounded-xl bg-[#d4d4d3] bg-opacity-30 backdrop-blur border border-white/30 flex flex-row items-center justify-center gap-x-6 relative">
        <div className="absolute top-4 right-4">
          <div className="flex flex-col items-end">
            {/* select box */}
            <div>
              <label htmlFor="language-select" className="text-white mr-2">
                Langues du corpus :
              </label>
              <select
                name="language"
                id="language-select"
                className="rounded px-3 py-1 text-black"
              >
                <option value="fr-en">FR / EN</option>
                <option value="fr-es">FR / ES</option>
                <option value="fr-ar">FR / AR</option>
              </select>
            </div>

            {/* separation line */}
            <hr className="border-t border-white/40 mt-2 w-full" />
          </div>
        </div>

        {/* files conteners */}
        <div className="w-1/2 flex justify-center">
          <label className="flex items-center gap-2 px-4 py-2 text-sm text-white backdrop-blur-md cursor-pointer hover:bg-white/20 transition rounded">
            <span>Choose File</span>
            <input
              type="file"
              onChange={(e) => console.log(e.target.files?.[0])}
              className="hidden"
            />
          </label>
        </div>
        <div className="h-3/5 w-px bg-white/40 mx-2"></div>
        <div className="w-1/2 flex justify-center">
          <label className="flex items-center gap-2 px-4 py-2 text-sm text-white backdrop-blur-md cursor-pointer hover:bg-white/20 transition rounded">
            <span>Choose File</span>
            <input
              type="file"
              onChange={(e) => console.log(e.target.files?.[0])}
              className="hidden"
            />
          </label>
        </div>
        <div className="absolute bottom-6 left-0 right-0 flex justify-center">
          <button
            type="submit"
            className="min-w-[200px] px-6 py-2 bg-white bg-opacity-20 text-white-400 rounded hover:bg-opacity-40 transition"
          >
            Compare
          </button>
        </div>
      </div>
    </div>
  );
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
          <button onClick={() => {
            setCount(count => count + 1);
            setCount(count => count + 1);}}>
          Double +1
        </button>
        <h2>  {count}</h2>
 
      </div>    
    </>
  )
}
