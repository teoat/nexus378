// This is a simple image loader that returns the src as is.
// This is required for Next.js when using a custom image loader.
export default function customImageLoader({ src }: { src: string; width: number; quality?: number; }) {
  return src;
}
