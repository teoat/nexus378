import { AppProps } from 'next/app';
import { ToastProvider } from '../components/ToastProvider';
import '../styles/globals.css'; // Assuming a global stylesheet exists

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <ToastProvider>
      <Component {...pageProps} />
    </ToastProvider>
  );
}

export default MyApp;