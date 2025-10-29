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
        types: ["restaurant", "cafe", "bakery"], // Restrict to business places
        componentRestrictions: { country: "de" }, // 🇩🇪 Germany only
      });

      // --- When user selects a place
      autoC.addListener("place_changed", async () => {
        const place = autoC.getPlace();
        if (!place?.place_id) return;

        setRestaurant(place);
        setLoading(true);

        try {
          const res = await axios.get(`${backendUrl}/recommend`, {
            params: { place_id: place.place_id },
          });
          setDishes(res.data.top_dishes || []);
        } catch (err) {
          console.error("Backend error:", err);
        } finally {
          setLoading(false);
        }
      });
    }
  }, []);

  return (
    <div className="min-h-screen flex flex-col items-center justify-start bg-primary text-accent relative">
      {/* --- Top Accent Bar --- */}
      <div
        style={{
          width: "100%",
          height: "1rem",
          backgroundColor: "#F2EAD3",
          position: "absolute",
          top: 0,
          left: 0,
        }}
      ></div>

      {/* --- Main content container --- */}
      <div className="flex flex-col items-center" style={{ marginTop: "5vh" }}>
        {/* --- Title + Subtitle --- */}
        <div className="text-center">
          <h1
            className="font-extrabold tracking-tight text-accent"
            style={{
              fontSize: "7rem",
              lineHeight: "1",
              margin: "0",
              marginTop: "1rem",
            }}
          >
            DishTip
          </h1>
          <p
            className="text-highlight font-medium"
            style={{
              fontSize: "1.2rem",
              marginTop: "1rem",
            }}
          >
            Discover the best dishes anywhere
          </p>
        </div>

        {/* --- Search Bar --- */}
        <div className="flex justify-center w-full" style={{ marginTop: "7rem" }}>
          <input
            ref={inputRef}
            id="search-bar"
            type="text"
            placeholder="Search for a restaurant..."
            className="search-input"
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="off"
            spellCheck={false}
            name="dishtip-search"
            inputMode="search"
            style={{
              width: "600px",
              padding: "1rem 1.2rem",
              borderRadius: "1rem",
              border: "2px solid #F4991A",
              fontSize: "1.1rem",
              outline: "none",
              boxShadow: "0 4px 12px rgba(0,0,0,0.06)",
            }}
          />
        </div>

        {/* --- Results Card --- */}
        <div
          className="flex flex-col items-center w-full"
          style={{ marginTop: "80px" }}
        >
          {loading && <Loader />}
          {restaurant && !loading && (
            <div
              className="bg-white shadow-soft rounded-xl border border-secondary/30 text-left"
              style={{
                width: "60%",
                maxWidth: "700px",
                padding: "2rem 2.5rem",
              }}
            >
              <h2 className="text-2xl font-semibold text-accent mb-2">
                Top Dishes at {restaurant.name}
              </h2>
              {dishes.length === 0 ? (
                <p className="text-accent/80">
                  No dish mentions found in recent reviews.
                </p>
              ) : (
                <DishList restaurant={restaurant} dishes={dishes} />
              )}
            </div>
          )}
        </div>
      </div>

      {/* --- Footer --- */}
      <footer
        className="text-sm text-accent/70"
        style={{ marginTop: "auto", padding: "60px 0" }}
      >
        Made with <span className="text-highlight">❤️</span> and good taste · DishTip ©{" "}
        {new Date().getFullYear()}
      </footer>
    </div>
  );
}
