import useSWR from 'swr';

class FetchError extends Error {
  info: any;
  status: number;

  constructor(message: string, info: any, status: number) {
    super(message);
    this.info = info;
    this.status = status;
  }
}

const fetcher = async (url: string) => {
  const res = await fetch(url);

  if (!res.ok) {
    const errorInfo = await res.json();
    throw new FetchError('An error occurred while fetching the data.', errorInfo, res.status);
  }

  return res.json();
};

export function useApi(endpoint: string | null) {
  const { data, error, isLoading, mutate } = useSWR(endpoint ? `/api${endpoint}` : null, fetcher);

  return {
    data,
    isLoading,
    isError: error,
    mutate,
  };
}