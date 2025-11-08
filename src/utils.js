export const relativeTime = (timestamp) => {
  if (!timestamp) return 'just now';
  const value = typeof timestamp?.toDate === 'function' ? timestamp.toDate().getTime() : Number(timestamp);
  if (!value) return 'just now';
  const diff = Date.now() - value;
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return 'moments ago';
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
};
