import { useState, useEffect, useRef } from 'react';

const backendUrl = import.meta.env.VITE_BACKEND_URL;
const googleKey = import.meta.env.VITE_GOOGLE_API_KEY;

export default function App() {
  const [restaurant, setRestaurant] = useState(null);
  const [dishes, setDishes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [displayCount, setDisplayCount] = useState(5);
  const [loadingEmoji, setLoadingEmoji] = useState('🍕');

  const inputRef = useRef(null);

  // Random emoji selector for loading animation
  const loadingEmojis = ['🍕', '🍣', '🍜', '🐟', '🦖', '🍷'];
  
  useEffect(() => {
    // Select random emoji when component mounts
    const randomEmoji = loadingEmojis[Math.floor(Math.random() * loadingEmojis.length)];
    setLoadingEmoji(randomEmoji);
  }, []);

  useEffect(() => {
    // Load Google Places script manually (only once)
    const scriptId = "google-places-script";
    if (!document.getElementById(scriptId)) {
      const script = document.createElement("script");
      script.id = scriptId;
      script.src = `https://maps.googleapis.com/maps/api/js?key=${googleKey}&libraries=places`;
      script.async = true;
      script.defer = true;
      document.body.appendChild(script);
      script.onload = initAutocomplete;
    } else {
      initAutocomplete();
    }

    function initAutocomplete() {
      if (!window.google || !window.google.maps) return;

      const autoC = new window.google.maps.places.Autocomplete(inputRef.current, {
        fields: ["place_id", "name", "formatted_address", "types"],
        types: ["restaurant", "cafe", "bakery", "bar"],
        componentRestrictions: { country: "de" },
      });

      // When user selects a place
      autoC.addListener("place_changed", async () => {
        const place = autoC.getPlace();
        if (!place?.place_id) return;

        setRestaurant(place);
        setLoading(true);
        setDisplayCount(5);
        
        // Select new random emoji for each search
        const randomEmoji = ['🍕', '🍣', '🍜', '🐟', '🦖', '🍷'][Math.floor(Math.random() * 6)];
        setLoadingEmoji(randomEmoji);

        try {
          const url = `${backendUrl}/recommendations/${place.place_id}`;
          const res = await fetch(url);
          const data = await res.json();

          console.log("🔥 Backend response:", data);

          // EXPECTED SHAPE:
          // { recommendations: [ { dish_name, author, source, timestamp, review_link, ranking }, ... ] }
          const dishesArray = data?.recommendations ?? [];
          setDishes(Array.isArray(dishesArray) ? dishesArray : []);
        } catch (err) {
          console.error("Backend error:", err);
          setDishes([]);
        } finally {
          setLoading(false);
        }
      });
    }
  }, []);

  const handleTryAgain = () => {
    window.location.reload();
  };

  const handleGiveFeedback = () => {
    window.open('YOUR_GOOGLE_FORM_URL', '_blank');
  };

  const handleLoadMore = () => {
    setDisplayCount(prev => prev + 5);
  };

  const formatTimeAgo = (timestamp) => {
    if (!timestamp) return '';
    try {
      // Check if timestamp is in seconds (Unix timestamp) and convert to milliseconds
      const timestampMs = timestamp < 10000000000 ? timestamp * 1000 : timestamp;
      const date = new Date(timestampMs);
      const now = new Date();
      const diffMs = now - date;
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      const diffMonths = Math.floor(diffDays / 30);
      const diffYears = Math.floor(diffDays / 365);

      if (diffYears > 0) {
        return `${diffYears} year${diffYears > 1 ? 's' : ''} ago`;
      } else if (diffMonths > 0) {
        return `${diffMonths} month${diffMonths > 1 ? 's' : ''} ago`;
      } else if (diffDays > 0) {
        return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
      } else {
        return 'today';
      }
    } catch {
      return '';
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col" style={{ fontFamily: '"Quicksand", "Rounded Mplus 1c", "Nunito", system-ui, sans-serif' }}>
      {/* Header */}
      <header className="shadow-sm" style={{ backgroundColor: '#7B113A' }}>
        <div className="max-w-2xl mx-auto px-4 py-4 flex justify-between items-center">
          <button 
            onClick={handleTryAgain}
            className="text-2xl font-bold hover:opacity-80 transition cursor-pointer text-white"
          >
            🍽️ DishTip
          </button>
          <button
            onClick={handleGiveFeedback}
            className="text-sm font-medium px-4 py-2 rounded-lg transition hover:opacity-80 bg-white"
            style={{ color: '#7B113A' }}
          >
            Give Feedback
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-2xl mx-auto px-4 py-8 w-full">
        {/* Search Bar */}
        {!restaurant && (
          <div className="space-y-6">
            <div className="text-center space-y-3 mb-8">
              <h2 className="text-3xl font-bold text-gray-800">
                Hey there, you snack!
              </h2>
              <p className="text-gray-600">
                Thanks for testing my graduation project! 👋 It's simple! Select a food spot and the app will recommend you dishes that other foodies loooove!
              </p>
            </div>
            <div className="relative">
              <input
                ref={inputRef}
                type="text"
                placeholder="Choose a nice food place here..."
                className="w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:outline-none text-base shadow-sm"
                style={{ borderColor: '#7B113A' }}
              />
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center space-y-6 py-12">
            {/* Animated Food Icons */}
            <div className="relative w-32 h-32 mx-auto">
              <div className="absolute inset-0 animate-spin" style={{ animationDuration: '2s' }}>
                <div className="absolute top-0 left-1/2 -translate-x-1/2 text-4xl">{loadingEmoji}</div>
              </div>
              <div className="absolute inset-0 animate-spin" style={{ animationDuration: '2s', animationDelay: '0.5s' }}>
                <div className="absolute top-0 left-1/2 -translate-x-1/2 text-4xl">{loadingEmoji}</div>
              </div>
              <div className="absolute inset-0 animate-spin" style={{ animationDuration: '2s', animationDelay: '1s' }}>
                <div className="absolute top-0 left-1/2 -translate-x-1/2 text-4xl">{loadingEmoji}</div>
              </div>
              <div className="absolute inset-0 animate-spin" style={{ animationDuration: '2s', animationDelay: '1.5s' }}>
                <div className="absolute top-0 left-1/2 -translate-x-1/2 text-4xl">{loadingEmoji}</div>
              </div>
            </div>
            
            <div className="space-y-2">
              <h3 className="text-lg font-semibold text-gray-800">
                Nom nom. Checking reviews and blogs for dishes mentioned...
              </h3>
              <p className="text-sm text-gray-600">Might take a few seconds ⏱️</p>
            </div>

            {/* Progress bar */}
            <div className="max-w-xs mx-auto">
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div 
                  className="h-full rounded-full animate-pulse"
                  style={{ 
                    backgroundColor: '#7B113A',
                    animation: 'progress 15s ease-in-out forwards'
                  }}
                ></div>
              </div>
            </div>

            <style>{`
              @keyframes progress {
                from { width: 0%; }
                to { width: 100%; }
              }
            `}</style>
          </div>
        )}

        {/* No Results */}
        {!loading && restaurant && dishes.length === 0 && (
          <div className="text-center space-y-4 py-12">
            <div className="text-gray-400 text-5xl mb-4">🤔</div>
            <h3 className="text-lg font-semibold text-gray-800">
              Hmm, this restaurant doesn't seem so popular...
            </h3>
            <p className="text-gray-600">No dish recommendations for this spot yet. Try another restaurant!</p>
            <button
              onClick={handleTryAgain}
              className="mt-4 px-6 py-2.5 rounded-lg font-medium transition hover:opacity-90 text-white bg-gray-700"
            >
              Search Again
            </button>
          </div>
        )}

        {/* Recommendations */}
        {dishes.length > 0 && (
          <div className="space-y-6">
            <div className="text-center space-y-2 mb-8 pb-4 border-b-2" style={{ borderColor: '#7B113A' }}>
              <p className="text-xl font-semibold" style={{ color: '#7B113A' }}>
                {restaurant?.name}
              </p>
              {restaurant?.formatted_address && (
                <p className="text-sm text-gray-600">{restaurant.formatted_address}</p>
              )}
            </div>

            <div className="space-y-4 max-w-lg mx-auto">
              {dishes.slice(0, displayCount).map((dish, index) => (
                <div
                  key={index}
                  className="bg-white rounded-lg shadow border-2 p-4 hover:shadow-md transition"
                  style={{ borderColor: '#7B113A' }}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex items-start gap-3 flex-1">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold text-white text-sm"
                           style={{ backgroundColor: '#7B113A' }}>
                        {index + 1}
                      </div>
                      <div className="flex-1 min-w-0">
                        <h3 className="text-lg font-bold mb-1 text-gray-800">
                          {dish.dish_name || `Dish ${index + 1}`}
                        </h3>
                        
                        <div className="space-y-0.5 text-sm text-gray-600">
                          {dish.author && (
                            <p className="truncate">
                              <span className="font-semibold">By:</span> {dish.author}
                            </p>
                          )}
                          {dish.source && (
                            <p className="truncate">
                              <span className="font-semibold">Source:</span> {dish.source}
                            </p>
                          )}
                          {dish.timestamp && (
                            <p className="text-gray-500 text-xs">
                              {formatTimeAgo(dish.timestamp)}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Link Icon Button */}
                    <div className="flex-shrink-0">
                      {dish.review_link ? (
                        <a
                          href={dish.review_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="w-9 h-9 rounded-full flex items-center justify-center transition hover:opacity-80"
                          style={{ backgroundColor: '#7B113A' }}
                          title="Read review"
                        >
                          <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                          </svg>
                        </a>
                      ) : (
                        <div
                          className="w-9 h-9 rounded-full flex items-center justify-center bg-gray-300"
                          title="No review available"
                        >
                          <svg className="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                          </svg>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Load More Button */}
            {displayCount < dishes.length && (
              <div className="text-center pt-4">
                <button
                  onClick={handleLoadMore}
                  className="px-6 py-2.5 rounded-lg font-medium transition hover:opacity-90 text-white"
                  style={{ backgroundColor: '#7B113A' }}
                >
                  Serve More Reviews
                </button>
              </div>
            )}

            <div className="text-center pt-6">
              <button
                onClick={handleTryAgain}
                className="px-8 py-3 rounded-lg font-semibold transition hover:opacity-90 text-white text-lg shadow-md bg-gray-700"
              >
                Search Again You Hungry Hippo
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t-2 py-4 mt-auto" style={{ borderColor: '#7B113A' }}>
        <div className="max-w-2xl mx-auto px-4 text-center text-sm text-gray-600">
          DishTip - Reducing food order anxiety ever since 2025 🍕
        </div>
      </footer>
    </div>
  );
}