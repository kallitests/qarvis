/** Builders pour générer des données de test lisibles et déterministes. */
export function buildTransactionNote(prefix = "qarvis"): string {
  return `${prefix}-${Date.now()}`;
}

export function randomAmount(min = 1, max = 100): string {
  return (Math.floor(Math.random() * (max - min + 1)) + min).toFixed(2);
}
