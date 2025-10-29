export default function DishList({ restaurant, dishes }) {
  return (
    <div className="mt-6 bg-white rounded-2xl shadow-soft p-6 w-96 border border-gray-100">
      <h2 className="text-2xl font-semibold mb-4 text-secondary">
        Top Dishes at <span className="text-accent">{restaurant.name}</span>
      </h2>
      {dishes.length ? (
        <ul className="space-y-3 text-left">
          {dishes.map((dish, i) => (
            <li key={i} className="flex items-center gap-2">
              <span className="text-accent text-lg">•</span>
              <span className="font-medium text-secondary">
                {dish.name.charAt(0).toUpperCase() + dish.name.slice(1)}
              </span>
              {dish.score && (
                <span className="text-sm text-gray-500">
                  ({dish.score.toFixed(2)})
                </span>
              )}
            </li>
          ))}
        </ul>
      ) : (
        <p className="text-gray-500">No dish mentions found in recent reviews.</p>
      )}
    </div>
  );
}
