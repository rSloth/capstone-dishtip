import { useState, useEffect, useRef } from 'react';

const backendUrl = import.meta.env.VITE_BACKEND_URL;
const googleKey = import.meta.env.VITE_GOOGLE_API_KEY;

export default function App() {
  const [restaurant, setRestaurant] = useState(null);
  const [dishes, setDishes] = useState([]);
  const [loading, setLoading] = useState(false);

  const inputRef = useRef(null);

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

  const formatDate = (timestamp) => {
    if (!timestamp) return '';
    try {
      const date = new Date(timestamp);
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
    } catch {
      return timestamp;
    }
  };

  return (
    <div className="min-h-screen bg-white flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b-2" style={{ borderColor: '#F45905' }}>
        <div className="max-w-2xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold" style={{ color: '#512C62' }}>
            🍽️ DishTip
          </h1>
          <button
            onClick={handleGiveFeedback}
            className="text-sm font-medium px-4 py-2 rounded-lg transition hover:opacity-80"
            style={{ backgroundColor: '#F45905', color: 'white' }}
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
              <h2 className="text-3xl font-bold" style={{ color: '#512C62' }}>
                Hello friend! 👋
              </h2>
              <p className="text-lg" style={{ color: '#F45905' }}>
                Ready to discover what to order?
              </p>
              <p className="text-gray-600">
                Tell us where you're eating, and we'll show you the crowd favorites!
              </p>
            </div>
            <div className="relative">
              <input
                ref={inputRef}
                type="text"
                placeholder="Search for a restaurant..."
                className="w-full px-4 py-3 border-2 rounded-lg focus:ring-2 focus:outline-none text-base shadow-sm"
                style={{ borderColor: '#512C62' }}
              />
            </div>
          </div>
        )}

        {/* Loading State */}
        {loading && (
          <div className="text-center space-y-4 py-12">
            <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2" style={{ borderColor: '#F45905' }}></div>
            <div className="space-y-2">
              <h3 className="text-lg font-semibold" style={{ color: '#512C62' }}>
                Cooking up some recommendations...
              </h3>
              <p className="text-gray-600">Digging through reviews and food blogs</p>
              <p className="text-sm text-gray-500">Takes about 10 seconds ⏱️</p>
            </div>
          </div>
        )}

        {/* No Results */}
        {!loading && restaurant && dishes.length === 0 && (
          <div className="text-center space-y-4 py-12">
            <div className="text-gray-400 text-5xl mb-4">🤔</div>
            <h3 className="text-lg font-semibold" style={{ color: '#512C62' }}>
              Hmm, couldn't find the secret sauce
            </h3>
            <p className="text-gray-600">No recommendations for this spot yet. Try another restaurant!</p>
            <button
              onClick={handleTryAgain}
              className="mt-4 px-6 py-2.5 rounded-lg font-medium transition hover:opacity-90 text-white"
              style={{ backgroundColor: '#F45905' }}
            >
              Try Another Restaurant
            </button>
          </div>
        )}

        {/* Recommendations - Menu Style */}
        {dishes.length > 0 && (
          <div className="space-y-6">
            <div className="text-center space-y-2 mb-8 pb-4 border-b-2" style={{ borderColor: '#F45905' }}>
              <h2 className="text-3xl font-bold" style={{ color: '#512C62' }}>
                Today's Favorites
              </h2>
              <p className="text-xl font-semibold" style={{ color: '#C70D3A' }}>
                {restaurant?.name}
              </p>
              {restaurant?.formatted_address && (
                <p className="text-sm text-gray-600">{restaurant.formatted_address}</p>
              )}
            </div>

            <div className="bg-white rounded-xl shadow-lg border-2 overflow-hidden" style={{ borderColor: '#512C62' }}>
              {dishes.slice(0, 5).map((dish, index) => (
                <div
                  key={index}
                  className="p-6 border-b border-gray-200 last:border-b-0 hover:bg-orange-50 transition"
                >
                  <div className="flex items-start gap-4">
                    <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center font-bold text-white text-lg"
                         style={{ backgroundColor: '#F45905' }}>
                      {index + 1}
                    </div>
                    <div className="flex-1">
                      <h3 className="text-xl font-bold mb-2" style={{ color: '#512C62' }}>
                        {dish.dish_name || `Dish ${index + 1}`}
                      </h3>
                      
                      <div className="space-y-1 mb-3 text-sm">
                        {dish.author && (
                          <p className="text-gray-700">
                            <span className="font-semibold" style={{ color: '#512C62' }}>
                              Recommended by:
                            </span>{' '}
                            {dish.author}
                          </p>
                        )}
                        {dish.source && (
                          <p className="text-gray-700">
                            <span className="font-semibold" style={{ color: '#512C62' }}>
                              Source:
                            </span>{' '}
                            {dish.source}
                          </p>
                        )}
                        {dish.timestamp && (
                          <p className="text-gray-600">
                            <span className="font-semibold">Date:</span> {formatDate(dish.timestamp)}
                          </p>
                        )}
                      </div>

                      {dish.review_link && (
                        <a
                          href={dish.review_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center text-sm font-medium hover:underline"
                          style={{ color: '#F45905' }}
                        >
                          Read full review →
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            <div className="text-center pt-6">
              <button
                onClick={handleTryAgain}
                className="px-8 py-3 rounded-lg font-semibold transition hover:opacity-90 text-white text-lg shadow-md"
                style={{ backgroundColor: '#F45905' }}
              >
                Find Another Restaurant
              </button>
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t-2 py-4 mt-auto" style={{ borderColor: '#512C62' }}>
        <div className="max-w-2xl mx-auto px-4 text-center text-sm text-gray-600">
          Powered by real reviews and food blogs 🍕
        </div>
      </footer>
    </div>
  );
}