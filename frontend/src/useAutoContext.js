import { useEffect, useState } from "react";

function computeTimeOfDay(date) {
  const h = date.getHours();
  if (h >= 5 && h < 12) return "morning";
  if (h >= 12 && h < 17) return "afternoon";
  if (h >= 17 && h < 21) return "evening";
  return "night";
}

function computeSeason(date) {
  const m = date.getMonth() + 1; // 1-12
  if (m >= 6 && m <= 9) return "monsoon";
  if (m >= 10 && m <= 11) return "post_monsoon";
  if (m >= 12 || m <= 2) return "winter";
  return "summer";
}

export default function useAutoContext() {
  const [context, setContext] = useState(() => {
    const now = new Date();
    return {
      time_of_day: computeTimeOfDay(now),
      season: computeSeason(now),
      lat: null,
      lng: null,
      locationStatus: "requesting", // requesting | granted | denied | unsupported
      district: "Unknown",
    };
  });

  useEffect(() => {
    // Keep time_of_day / season fresh (cheap, no permission needed)
    const interval = setInterval(() => {
      const now = new Date();
      setContext((prev) => ({
        ...prev,
        time_of_day: computeTimeOfDay(now),
        season: computeSeason(now),
      }));
    }, 60_000);

    if (!navigator.geolocation) {
      setContext((prev) => ({ ...prev, locationStatus: "unsupported" }));
      return () => clearInterval(interval);
    }

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        setContext((prev) => ({
          ...prev,
          lat: pos.coords.latitude,
          lng: pos.coords.longitude,
          locationStatus: "granted",
        }));
      },
      () => {
        setContext((prev) => ({ ...prev, locationStatus: "denied" }));
      },
      { enableHighAccuracy: true, timeout: 8000 }
    );

    return () => clearInterval(interval);
  }, []);

  return context;
}
