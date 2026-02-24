export default function PageWrapper({ children }: { children: React.ReactNode }) {
  return (
    <main className="pt-16 md:pt-16 min-h-screen">
      {children}
    </main>
  );
}
