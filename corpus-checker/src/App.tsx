import { useEffect, useState } from "react";
import Particles from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import { tsParticles } from "@tsparticles/engine";
import DragDrop from "./DropZone";

export default function App() {
  const [fileFR, setFileFR] = useState<File | null>(null);
  const [fileEN, setFileEN] = useState<File | null>(null);
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
                className="rounded px-3 py-1 text-black bg-white"
              >
                <option value="fr-en">🇫🇷 / 🇬🇧</option>
                <option value="fr-es">🇫🇷 / 🇪🇸</option>
                <option value="fr-ar">🇫🇷 / 🇸🇦</option>
              </select>
            </div>

            {/* separation line */}
            <hr className="border-t border-white/40 mt-2 w-full" />
          </div>
        </div>
        {/* used the componant DragDrop from the dropzone */}
        <div className="flex items-stretch h-48 w-35 ">
          <DragDrop
            file={fileFR}
            setFile={setFileFR}
            label="Select your FR file or drag and drop it"
          />
          <div className="h-15 w-px bg-white/40 mx-2"></div>
          <DragDrop
            file={fileEN}
            setFile={setFileEN}
            label="Select your EN file or drag and drop it"
          />
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
}
