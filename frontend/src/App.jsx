import { useState, useEffect, useRef } from "react";
import axios from "axios";
import DishList from "./components/DishList";
import Loader from "./components/Loader";

const backendUrl = import.meta.env.VITE_BACKEND_URL;
const googleKey = import.meta.env.VITE_GOOGLE_API_KEY;

export default function App() {
  const [restaurant, setRestaurant] = useState(null);
  const [dishes, setDishes] = useState([]);
  const [loading, setLoading] = useState(false);

  const inputRef = useRef(null);

  useEffect(() => {
    // --- Load Google Places script manually (only once)
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
        types: ["restaurant", "cafe", "bakery", "bar"],              // business places
        componentRestrictions: { country: "de" }, // 🇩🇪 Germany only
      });

      // When user selects a place
      autoC.addListener("place_changed", async () => {
        const place = autoC.getPlace();
        if (!place?.place_id) return;

        setRestaurant(place);
        setLoading(true);

        try {
          const url = `${backendUrl}/recommendations/${place.place_id}`;
          const res = await axios.get(url);

          console.log("🔥 Backend response:", res.data);

          // EXPECTED SHAPE:
          // { recommendations: [ { dish_name, author, source, timestamp, review_link, ranking }, ... ] }
          const dishesArray = res?.data?.recommendations ?? [];
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

  return (
    <div className="min-h-screen flex flex-col items-center justify-start bg-primary text-accent relative">
      {/* Top Accent Bar */}
      <div className="w-full h-4 bg-secondary absolute top-0 left-0" />

      {/* Main content */}
      <div className="flex flex-col items-center mt-[5vh]">
        {/* Title + Subtitle */}
        <div className="text-center">
          <h1 className="font-extrabold tracking-tight text-accent text-[7rem] leading-none mt-4 m-0">
            DishTip
          </h1>
          <p className="text-highlight font-medium text-[1.2rem] mt-4">
            Discover the best dishes anywhere
          </p>
        </div>

        {/* Search Bar */}
        <div className="flex justify-center w-full mt-28">
          <input
            ref={inputRef}
            id="search-bar"
            type="text"
            placeholder="Search for a restaurant..."
            className="w-[600px] max-w-full p-4 px-5 rounded-2xl border-2 border-highlight text-accent bg-primary outline-none shadow-soft focus:ring-4 focus:ring-highlight/20 focus:border-highlight placeholder:text-accent/40"
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="off"
            spellCheck={false}
            name="dishtip-search"
            inputMode="search"
          />
        </div>

        {/* Results Card */}
        <div className="flex flex-col items-center w-full mt-20">
          {loading && <Loader />}

          {restaurant && !loading && (
            <div className="w-[60%] max-w-[700px] bg-white shadow-soft rounded-xl border border-secondary/30 text-left p-10">
              <h2 className="text-2xl font-semibold text-accent mb-6">
                🍴 Top Dishes at {restaurant.name}
              </h2>

              {(!dishes || dishes.length === 0) ? (
                <p className="text-accent/80">No dish mentions found in recent reviews.</p>
              ) : (
                dishes.slice(0, 5).map((dish, idx) => {
                  const date = dish.timestamp
                    ? new Date(dish.timestamp * 1000).toLocaleDateString("de-DE", {
                        day: "2-digit",
                        month: "2-digit",
                        year: "2-digit",
                      })
                    : "unbekannt";

                  return (
                    <div
                      key={`${dish.dish_name}-${idx}`}
                      className="mb-4 p-4 rounded-lg border border-secondary bg-primary hover:shadow-md transition-all duration-150"
                    >
                      <h3 className="text-xl font-semibold text-accent mb-1 capitalize">
                        {dish.dish_name}
                      </h3>
                      <p className="text-accent/80 text-sm">
                        recommended by{" "}
                        <span className="font-medium text-accent">{dish.author || "Anonymous"}</span>
                      </p>
                      <p className="text-accent/70 text-sm italic">
                        written on {dish.source || "unknown"}, {date}
                      </p>
                    </div>
                  );
                })
              )}
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <footer className="text-sm text-accent/70 mt-auto py-14">
        Made with <span className="text-highlight">❤️</span> and good taste · DishTip ©{" "}
        {new Date().getFullYear()}
      </footer>
    </div>
  );
}