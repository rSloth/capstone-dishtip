export default function Loader() {
  return (
    <div className="mt-8 w-80 bg-white rounded-xl shadow-soft p-6 border border-gray-100 animate-pulse">
      <div className="space-y-3">
        <div className="h-4 bg-gray-200 rounded w-3/4 mx-auto"></div>
        <div className="h-4 bg-gray-200 rounded w-full mx-auto"></div>
        <div className="h-4 bg-gray-200 rounded w-5/6 mx-auto"></div>
      </div>
      <p className="mt-4 text-accent font-medium">Analyzing reviews...</p>
    </div>
  );
}
