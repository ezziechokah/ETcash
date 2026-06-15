export function unwrapList(data) {
  if (Array.isArray(data)) return data;
  return data?.results ?? [];
}
