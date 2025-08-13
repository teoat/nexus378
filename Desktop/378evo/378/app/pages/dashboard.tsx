import type { NextPage } from 'next';
import Head from 'next/head';
import { WebSocketProvider } from '../components/WebSocketProvider';
import DashboardGrid from '../components/DashboardGrid';
import StatusIndicatorWidget from '../components/StatusIndicatorWidget';
import ProgressWidget from '../components/ProgressWidget';

const Dashboard: NextPage = () => {
  // Assume we have a caseId from the page context or a selector
  const caseId = 'mock-case-id'; // Replace with real logic to get the current caseId

  const handleTriggerAnalysis = async () => {
    try {
      const response = await fetch('/api/discrepancies/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ caseId }),
      });

      if (!response.ok) {
        throw new Error('Failed to trigger analysis');
      }

      const result = await response.json();
      alert(result.message);
    } catch (error) {
      console.error('Analysis trigger failed:', error);
      alert('Failed to trigger analysis.');
    }
  };

  return (
    <WebSocketProvider>
      <div>
        <Head>
          <title>Live Operations Dashboard</title>
          <meta name="description" content="Live Operations Dashboard" />
          <link rel="icon" href="/favicon.ico" />
        </Head>

        <main>
          <h1>
            Live Operations Dashboard
          </h1>
          <button onClick={handleTriggerAnalysis} style={{ marginBottom: '20px' }}>
            Trigger Discrepancy Analysis
          </button>
          <DashboardGrid>
            <StatusIndicatorWidget serviceName="API Gateway" status="Online" />
            <StatusIndicatorWidget serviceName="Python AI Service" status="Online" />
            <StatusIndicatorWidget serviceName="PostgreSQL" status="Degraded" />
            <StatusIndicatorWidget serviceName="Neo4j" status="Offline" />
            <ProgressWidget jobName="Parsing statement.pdf" progress={78} />
          </DashboardGrid>
        </main>
      </div>
    </WebSocketProvider>
  );
};

export default Dashboard;