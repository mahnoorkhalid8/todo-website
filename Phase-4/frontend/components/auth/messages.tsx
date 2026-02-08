interface MessageProps {
  type: 'success' | 'error' | 'info';
  message: string;
}

export default function Message({ type, message }: MessageProps) {
  if (!message) return null;

  const styles = {
    success: 'bg-green-100 border border-green-400 text-green-700',
    error: 'bg-red-100 border border-red-400 text-red-700',
    info: 'bg-blue-100 border border-blue-400 text-blue-700',
  };

  return (
    <div className={`${styles[type]} px-4 py-3 rounded mb-4`} role="alert">
      <span className="block sm:inline">{message}</span>
    </div>
  );
}