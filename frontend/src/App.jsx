import { useState, useEffect, useRef } from 'react';
import { Plus, RefreshCcw } from "lucide-react"; // ⬅️ add this import at the top
import { Analytics } from "@vercel/analytics/next"

const backendUrl = import.meta.env.VITE_BACKEND_URL;
const googleKey = import.meta.env.VITE_GOOGLE_API_KEY;

export default function App() {
  const [restaurant, setRestaurant] = useState(null);
  const [restaurantInfo, setRestaurantInfo] = useState(null);
  const [dishes, setDishes] = useState([]);
  const [loading, setLoading] = useState(false);
  const [displayCount, setDisplayCount] = useState(5);
  const [loadingEmoji, setLoadingEmoji] = useState('🍕');
  const [usedPriceLabels, setUsedPriceLabels] = useState([]);
  const [dishPrices, setDishPrices] = useState([]);

  const inputRef = useRef(null);

  const loadingEmojis = ['🍕', '🍣', '🍜', '🐟', '🦖', '🍷'];
  const priceLabels = [
    'some money', 'lots of money', 'expensive', 'cheap', 'good price', 
    'schnäppchen', 'bargain', 'worth it', 'priceless', 'will ruin you', 
    'not enough', "doesn't matter", 'holy cow', 'daddy pays', "don't look"
  ];
  
  const getRandomPrice = () => {
    const available = priceLabels.filter(p => !usedPriceLabels.includes(p));
    if (available.length === 0) {
      setUsedPriceLabels([]);
      return priceLabels[Math.floor(Math.random() * priceLabels.length)];
    }
    const selected = available[Math.floor(Math.random() * available.length)];
    setUsedPriceLabels(prev => [...prev, selected]);
    return selected;
  };
  
  useEffect(() => {
    const randomEmoji = loadingEmojis[Math.floor(Math.random() * loadingEmojis.length)];
    setLoadingEmoji(randomEmoji);
  }, []);

  useEffect(() => {
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

      autoC.addListener("place_changed", async () => {
        const place = autoC.getPlace();
        if (!place?.place_id) return;

        setRestaurant(place);
        setLoading(true);
        setDisplayCount(5);
        setRestaurantInfo(null);
        setUsedPriceLabels([]);
        
        const randomEmoji = ['🍕', '🍣', '🍜', '🐟', '🦖', '🍷'][Math.floor(Math.random() * 6)];
        setLoadingEmoji(randomEmoji);

        try {
          const infoUrl = `${backendUrl}/restaurant_info/${place.place_id}`;
          const infoRes = await fetch(infoUrl);
          const infoData = await infoRes.json();
          setRestaurantInfo(infoData.restaurant_info);

          const recUrl = `${backendUrl}/recommendations/${place.place_id}`;
          const recRes = await fetch(recUrl);
          const recData = await recRes.json();

          const dishesArray = recData?.recommendations ?? [];
          setDishes(Array.isArray(dishesArray) ? dishesArray : []);
          const prices = dishesArray.map(() => getRandomPrice());
          setDishPrices(prices);
        } catch (err) {
          console.error("Backend error:", err);
          setDishes([]);
        } finally {
          setLoading(false);
        }
      });
    }
  }, []);

  const handleTryAgain = () => window.location.reload();
  const handleGiveFeedback = () => {
  const restaurantName = restaurantInfo?.name || restaurant?.name || "";
  const topDishes = dishes
    .slice(0, 5)
    .map(d => d.dish_name)
    .filter(Boolean)
    .join(", ");

  const feedbackUrl = `https://docs.google.com/forms/d/e/1FAIpQLSdGZ9tCVAsPNum3nPdU6qrl2YhjbEe5cKA6pdMY620Kg7CWhA/viewform?usp=pp_url&entry.28632495=${encodeURIComponent(restaurantName)}&entry.1243942471=${encodeURIComponent(topDishes)}`;

  window.open(feedbackUrl, "_blank");
};

  const handleLoadMore = () => setDisplayCount(prev => prev + 5);

  const formatTimeAgo = (timestamp) => {
    if (!timestamp) return '';
    try {
      const timestampMs = timestamp < 10000000000 ? timestamp * 1000 : timestamp;
      const date = new Date(timestampMs);
      const now = new Date();
      const diffMs = now - date;
      const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
      const diffMonths = Math.floor(diffDays / 30);
      const diffYears = Math.floor(diffDays / 365);

      if (diffYears > 0) return `${diffYears} year${diffYears > 1 ? 's' : ''} ago`;
      if (diffMonths > 0) return `${diffMonths} month${diffMonths > 1 ? 's' : ''} ago`;
      if (diffDays > 0) return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
      return 'today';
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
            DishTip
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
          <div className="space-y-6 bg-gradient-to-b from-[#7B113A]/10 via-white to-white rounded-lg py-20">
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
            <div className="relative w-32 h-32 mx-auto">
              {[0, 0.5, 1, 1.5].map((d, i) => (
                <div key={i} className="absolute inset-0 animate-spin" style={{ animationDuration: '2s', animationDelay: `${d}s` }}>
                  <div className="absolute top-0 left-1/2 -translate-x-1/2 text-4xl">{loadingEmoji}</div>
                </div>
              ))}
            </div>
            <div className="space-y-2">
              <h3 className="text-lg font-semibold text-gray-800">
                Nom nom. Checking reviews and blogs for dishes mentioned...
              </h3>
              <p className="text-sm text-gray-600">Might take a few seconds ⏱️</p>
            </div>
            <div className="max-w-xs mx-auto">
              <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                <div
                  className="h-full rounded-full animate-pulse"
                  style={{
                    backgroundColor: '#7B113A',
                    animation: 'progress 15s ease-in-out forwards',
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
            {/* Menu Header */}
            <div className="text-center space-y-3 mb-6 pb-6 border-b-4 border-double" style={{ borderColor: '#D4AF37' }}>
              <div className="flex items-center justify-center gap-3 mb-2">
                <div className="h-px w-16 bg-gradient-to-r from-transparent via-gray-400 to-gray-400"></div>
                <span className="text-3xl">🍽️</span>
                <div className="h-px w-16 bg-gradient-to-l from-transparent via-gray-400 to-gray-400"></div>
              </div>
              
              {restaurantInfo?.website_url ? (
                <div>
                  <a
                    href={restaurantInfo.website_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-3xl font-bold hover:underline cursor-pointer block"
                    style={{ color: '#7B113A', fontFamily: 'serif' }}
                  >
                    {restaurantInfo?.name || restaurant?.name}
                  </a>
                </div>
              ) : (
                <p className="text-3xl font-bold" style={{ color: '#7B113A', fontFamily: 'serif' }}>
                  {restaurantInfo?.name || restaurant?.name}
                </p>
              )}
              
              {(restaurantInfo?.address || restaurant?.formatted_address) && (
                <div>
                  {restaurantInfo?.google_maps_url ? (
                    <a
                      href={restaurantInfo.google_maps_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-gray-600 hover:underline cursor-pointer italic"
                    >
                      {restaurantInfo?.address || restaurant?.formatted_address}
                    </a>
                  ) : (
                    <p className="text-sm text-gray-600 italic">
                      {restaurantInfo?.address || restaurant?.formatted_address}
                    </p>
                  )}
                </div>
              )}
              
              <div className="mt-8 mb-4 text-center">
                <span
                  className="text-2xl font-bold uppercase tracking-widest"
                  style={{ color: '#D4AF37' }}
                >
                  Today's Favorites
                </span>
              </div>
            </div>

            {/* Dish List */}
            <div className="max-w-2xl mx-auto bg-amber-50 rounded-lg shadow-lg border-2 p-8" style={{ borderColor: '#D4AF37' }}>
              <div className="space-y-6">
                {dishes.slice(0, displayCount).map((dish, index) => (
                  <div key={index} className="pb-6 last:pb-0">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-bold text-gray-900 uppercase whitespace-nowrap">
                        {dish.dish_name || `Dish ${index + 1}`}
                      </h3>
                      <div className="flex-1 border-b border-dotted border-gray-400 self-center"></div>
                      <span className="text-xs font-medium text-gray-600 whitespace-nowrap italic">
                        {dishPrices[index]}
                      </span>
                    </div>
                    <div className="text-sm text-gray-600 italic space-y-1 ml-1">
                      {dish.author && (
                        <p><span className="font-normal">Recommended by</span> {dish.author}</p>
                      )}
                      {dish.source && (
                        <p>
                          <span className="font-normal">As seen in</span>{' '}
                          {dish.review_link ? (
                            <a
                              href={dish.review_link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="hover:underline font-medium"
                              style={{ color: '#7B113A' }}
                            >
                              {dish.source}
                            </a>
                          ) : (
                            <span className="font-medium">{dish.source}</span>
                          )}
                        </p>
                      )}
                      {dish.timestamp && (
                        <p className="text-gray-500 text-xs">{formatTimeAgo(dish.timestamp)}</p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>

{/* Buttons */}
<div className="flex justify-center gap-4 pt-6">
  <button
    onClick={handleLoadMore}
    disabled={displayCount >= dishes.length}
    className={`flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg font-medium transition text-white ${
      displayCount >= dishes.length
        ? 'bg-gray-400 cursor-not-allowed opacity-70'
        : 'hover:opacity-90'
    }`}
    style={{
      backgroundColor: displayCount >= dishes.length ? '#9CA3AF' : '#7B113A',
    }}
  >
    <Plus size={18} />
    Serve More Reviews
  </button>

  <button
    onClick={handleTryAgain}
    className="flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg font-semibold transition hover:opacity-90 text-white shadow-md"
    style={{ backgroundColor: '#C46A7B' }}
  >
    <RefreshCcw size={18} />
    Search Again, Hungry Hippo
  </button>
</div>

          </div>
        )}
      </main>

      <footer className="bg-white border-t-2 py-4 mt-auto" style={{ borderColor: '#7B113A' }}>
        <div className="max-w-2xl mx-auto px-4 text-center text-sm text-gray-600">
          DishTip - Reducing food order anxiety ever since 2025 🍕
        </div>
      </footer>
    </div>
  );
}
