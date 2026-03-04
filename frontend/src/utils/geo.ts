/** Haversine distance between two lat/lng points in km. */
export function haversineKm(
  lat1: number, lng1: number,
  lat2: number, lng2: number,
): number {
  const R = 6371
  const dLat = ((lat2 - lat1) * Math.PI) / 180
  const dLng = ((lng2 - lng1) * Math.PI) / 180
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) *
      Math.cos((lat2 * Math.PI) / 180) *
      Math.sin(dLng / 2) ** 2
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
}

/** Theoretical minimum latency (speed of light in fiber ≈ 200 km/ms). */
export function theoreticalLatencyMs(
  lat1: number, lng1: number,
  lat2: number, lng2: number,
): number {
  return haversineKm(lat1, lng1, lat2, lng2) / 200
}
