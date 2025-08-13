
import { performance } from '@/lib/firebase';
import { trace, PerformanceTrace } from 'firebase/performance';

/**
 * Wraps a function with a Firebase Performance custom trace.
 * This allows for detailed monitoring of specific, critical operations.
 * 
 * @param traceName The name of the custom trace (e.g., "run_initial_matching").
 * @param fn The async function to execute and trace.
 * @returns The result of the wrapped function.
 */
export async function withPerformanceTrace<T>(
    traceName: string,
    fn: (traceInstance: PerformanceTrace) => Promise<T>
): Promise<T> {
    if (!performance) {
        // Performance Monitoring is not available, run the function directly.
        // Pass a mock trace object that does nothing to avoid runtime errors.
        const mockTrace = {
            start: () => {},
            stop: () => {},
            putMetric: () => {},
            putAttribute: () => {},
        } as unknown as PerformanceTrace;
        return fn(mockTrace);
    }

    const t = trace(performance, traceName);
    t.start();

    try {
        const result = await fn(t);
        t.stop();
        return result;
    } catch (error) {
        // Ensure the trace is stopped even if the function fails.
        t.stop();
        throw error;
    }
}

    