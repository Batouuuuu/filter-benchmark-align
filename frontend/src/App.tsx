import { useEffect, useState } from "react";
import Particles from "@tsparticles/react";
import { loadSlim } from "@tsparticles/slim";
import { tsParticles } from "@tsparticles/engine";
import DragDrop from "./DropZone";

export default function App() {
  const [fileFR, setFileFR] = useState<File | null>(null);
  const [fileEN, setFileEN] = useState<File | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [results, setResults] = useState<{
    initial: number;
    filtered: number;
    rejected: number;
    filter: string;
  } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async () => {
    if (!fileFR || !fileEN) {
      alert("Thanks to select two files");
      return;
    }
    
    setIsLoading(true);
    setShowModal(true);
    
    const formData = new FormData();
    formData.append("file_src", fileFR);
    formData.append("file_target", fileEN);

    try {
      const response = await fetch("http://localhost:8000/files", {
        method: "POST",
        body: formData,
      });
      
      const data = await response.json();
      if (data.status === "success") {
        setResults({
          initial: data.initial_sentence_count,
          filtered: data.filtered_sentence_count,
          rejected: data.rejected_count,
          filter: data.filter_used,
        });
      }
    } catch (error) {
      console.error("Error:", error);
      alert("An error occurred during processing");
    } finally {
      setIsLoading(false);
    }
  };

  // used for particles effect library
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
            onClick={handleSubmit} // call submit fuction
            className="min-w-[200px] px-6 py-2 bg-white bg-opacity-20 text-white-400 rounded hover:bg-opacity-40 transition"
          >
            Compare
          </button>
        </div>
      </div>
      {showModal && (
        <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50 z-50">
          <div className="bg-[#d4d4d3] rounded-lg p-6 w-[90%] max-w-lg max-h-[90vh] text-center shadow-lg overflow-y-auto">
            {isLoading ? (
              <>
                <h2 className="text-xl font-semibold mb-4">Analyse en cours</h2>
                <p className="mb-4">
                  Nous comparons vos fichiers. Veuillez patienter...
                </p>
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500 mx-auto my-4"></div>
              </>
            ) : results ? (
              <>
                <h2 className="text-xl font-semibold mb-4">Résultats de l'analyse</h2>
                
                <div className="grid grid-cols-3 gap-4 mb-6">
                  <div className="bg-white bg-opacity-20 p-4 rounded">
                    <h3 className="font-medium">Phrases initiales</h3>
                    <p className="text-2xl">{results.initial}</p>
                  </div>
                  <div className="bg-white bg-opacity-20 p-4 rounded">
                    <h3 className="font-medium">Phrases conservées</h3>
                    <p className="text-2xl text-green-500">{results.filtered}</p>
                    <p className="text-sm">
                      ({Math.round((results.filtered / results.initial) * 100)}%)
                    </p>
                  </div>
                  <div className="bg-white bg-opacity-20 p-4 rounded">
                    <h3 className="font-medium">Phrases rejetées</h3>
                    <p className="text-2xl text-red-500">{results.rejected}</p>
                    <p className="text-sm">
                      ({Math.round((results.rejected / results.initial) * 100)}%)
                    </p>
                  </div>
                </div>
                
                <div className="mb-4">
                  <h3 className="font-medium">Filtre appliqué</h3>
                  <p className="text-sm bg-white bg-opacity-20 p-2 rounded">
                    {results.filter}
                  </p>
                </div>
                
                <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
                  <div 
                    className="bg-blue-600 h-4 rounded-full" 
                    style={{
                      width: `${(results.filtered / results.initial) * 100}%`
                    }}
                  ></div>
                </div>
                
                <button
                  onClick={() => {
                    setShowModal(false);
                    setResults(null);
                  }}
                  className="mt-4 px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition"
                >
                  Nouvelle analyse
                </button>
              </>
            ) : (
              <>
                <h2 className="text-xl font-semibold mb-4">Erreur</h2>
                <p className="mb-4">
                  Une erreur est survenue lors du traitement.
                </p>
                <button
                  onClick={() => setShowModal(false)}
                  className="mt-2 px-4 py-2 bg-gray-200 hover:bg-gray-300 rounded"
                >
                  Fermer
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

