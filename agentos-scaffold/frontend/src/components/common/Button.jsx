export default function Button({ children, ...props }) {
  return (
    <button
      className="rounded-md bg-accent px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-50"
      {...props}
    >
      {children}
    </button>
  );
}
