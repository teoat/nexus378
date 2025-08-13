export const mockApi = {
  getCases: async () => {
    return Promise.resolve([
      { id: '1', name: 'Case 1', description: 'This is a mock case.' },
      { id: '2', name: 'Case 2', description: 'This is another mock case.' },
    ]);
  },
  createCase: async (data: { name: string; description: string }) => {
    return Promise.resolve({ id: '3', ...data });
  },
};