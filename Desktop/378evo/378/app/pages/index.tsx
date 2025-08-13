import type { NextPage } from 'next';
import Head from 'next/head';
import SignUpForm from '../components/SignUpForm';

const Home: NextPage = () => {
  return (
    <div>
      <Head>
        <title>Forensic Analysis Platform</title>
        <meta name="description" content="Forensic Analysis Platform" />
        <link rel="icon" href="/favicon.ico" />
      </Head>

      <main>
        <h1>
          Welcome to the Forensic Analysis Platform
        </h1>
        <SignUpForm />
      </main>
    </div>
  );
};

export default Home;