// Drag and drop component

type DragDropProps = {
  file: File | null;
  setFile: (file: File | null) => void;
  label?: string;
};

export default function DragDrop({ file, setFile, label }: DragDropProps) {
  const handleFile = (file: File) => {
    if (file.name.endsWith(".txt")) {
      setFile(file);
    } else {
      alert("only .txt files accepted.");
    }
  };

  return (
    <div
      className="w-1/2 flex justify-center drop-zone"
      onDragOver={(e) => e.preventDefault()}
      onDrop={(e) => {
        e.preventDefault();
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile) handleFile(droppedFile);
      }}
    >
      <label className="flex items-center gap-2 px-4 py-2 text-sm text-white backdrop-blur-md cursor-pointer hover:bg-white/20 transition rounded">
        {!file && <p>{label || "Select your file, or drag and drop it"}</p>}
        {file && <p className="text-white mt-2 text-xs">File : {file.name}</p>}
        <input
          type="file"
          accept=".txt"
          onChange={(e) => {
            const selectedFile = e.target.files?.[0];
            if (selectedFile) handleFile(selectedFile);
          }}
          className="hidden"
        />
      </label>
    </div>
  );
}
