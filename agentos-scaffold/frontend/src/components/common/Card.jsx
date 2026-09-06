export default function Card({ children, className = "" }) {
  return (
    <div className={`rounded-lg border border-white/10 bg-surface p-4 ${className}`}>
      {children}
    </div>
  );
}
