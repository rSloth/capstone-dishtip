# 🍽️ DishTip — Frontend

The **DishTip Frontend** is a clean, responsive React application that helps users instantly discover the *most loved dishes* at any restaurant — powered by live Google data and NLP intelligence from the DishTip backend.

Simply type a restaurant name into the Google-powered search bar, and DishTip will fetch and display the top 5 dishes mentioned positively in real customer reviews. ✨

---

## 🧠 Overview

The frontend is built with **React**, **Vite**, and **Tailwind CSS**, designed for speed, elegance, and easy integration with the DishTip backend.

It handles:

* 🧭 Autocomplete search via **Google Places API**
* 📡 Communication with the **FastAPI backend**
* 🎨 Responsive UI with a modern aesthetic
* 💬 Dynamic rendering of top dishes, reviewers, and sources

---

## 🧩 System Architecture

```
User → React Frontend
          ↓
   Google Places API (Autocomplete)
          ↓
   FastAPI Backend (Dish Extraction)
          ↓
     NLP Model (Flan-T5)
          ↓
     JSON Response → Rendered Dishes
```

---

## 🧰 Tech Stack

| Layer           | Technology        | Purpose                         |
| --------------- | ----------------- | ------------------------------- |
| **Framework**   | React + Vite      | Fast and modular frontend       |
| **Styling**     | Tailwind CSS      | Utility-first responsive design |
| **APIs**        | Google Places API | Restaurant lookup               |
| **Backend**     | FastAPI           | Provides dish recommendations   |
| **HTTP Client** | Axios             | Handles API calls               |
| **Deployment**  | Netlify / Vercel  | Frontend hosting                |

---

## 💻 Folder Structure

```
frontend/
│
├── src/
│   ├── components/
│   │   ├── DishList.jsx          # List display for dishes
│   │   ├── Loader.jsx            # Loading spinner
│   │   └── index.js
│   ├── styles/
│   │   └── index.css             # Tailwind styles + custom palette
│   ├── App.jsx                   # Main React app
│   └── main.jsx                  # Vite entry point
│
├── .env.example
├── index.html
├── package.json
├── tailwind.config.js
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repo

```bash
git clone https://github.com/<yourusername>/dishtip-frontend.git
cd dishtip-frontend
```

### 2️⃣ Install dependencies

```bash
npm install
```

### 3️⃣ Create your `.env` file

Copy `.env.example` → `.env` and add your API keys:

```bash
VITE_GOOGLE_API_KEY=your_google_api_key_here
VITE_BACKEND_URL=http://127.0.0.1:8000
```

### 4️⃣ Start the dev server

```bash
npm run dev
```

Then open your browser at [http://localhost:5173](http://localhost:5173).

---

## 🔑 Environment Variables

| Variable              | Description                                                |
| --------------------- | ---------------------------------------------------------- |
| `VITE_GOOGLE_API_KEY` | Your Google Maps / Places API key                          |
| `VITE_BACKEND_URL`    | URL of the FastAPI backend (e.g., `http://127.0.0.1:8000`) |

---

## 🧠 How It Works

1. The user types a restaurant name into the search bar.
2. Google’s **Places Autocomplete API** suggests restaurants in real time.
3. Once selected, the **place_id** is sent to the backend.
4. The backend fetches Google reviews, extracts dish mentions, and returns the top 5.
5. The frontend displays these dishes beautifully — with author, source, and review date.

---

## 🎨 UI Design

The app uses a custom warm-neutral color palette:

| Element               | Color     | Example          |
| --------------------- | --------- | ---------------- |
| **Background**        | `#F9F5F0` | soft beige       |
| **Accent (Gold)**     | `#F4991A` | golden highlight |
| **Secondary (Green)** | `#344F1F` | olive green      |
| **Highlight**         | `#F2EAD3` | light warm tone  |

The layout focuses on **minimalism, whitespace, and readability** — with a large central search bar and card-based result display.

---

## 📡 Example Response (from Backend)

```json
{
  "restaurant": "Brasserie Torbar",
  "recommendations": [
    {
      "dish_name": "truffle risotto",
      "author": "Yusuf Hadi",
      "source": "google",
      "timestamp": 1759338734
    },
    {
      "dish_name": "filet mignon",
      "author": "George Frewat",
      "source": "google",
      "timestamp": 1755985423
    }
  ]
}
```

---

## 🚀 Deployment

DishTip Frontend can be deployed on **Vercel**, **Netlify**, or **Render** easily.

Example (Vercel):

```bash
vercel deploy --prod
```

Make sure to set your environment variables in your hosting provider:

* `VITE_GOOGLE_API_KEY`
* `VITE_BACKEND_URL`

---

## 🧩 Future Enhancements

* 🍳 Display dish images using Google Vision API
* 🗺️ Show restaurant location on a mini-map
* 💬 Add filters (vegan, spicy, dessert, etc.)
* 🌎 Multi-language support for international users

---

## 🧑‍🍳 Credits

Built with ❤️ using **React**, **Tailwind**, and **Google Places API**.
Part of the **DishTip** project — where **data meets delicious.**