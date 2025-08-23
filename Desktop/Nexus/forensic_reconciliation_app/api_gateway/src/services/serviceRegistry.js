const services = {
  '/api/users': 'http://forensic_app:8000/users',
  '/api/transactions': 'http://forensic_app:8000/transactions',
  '/api/fraud': 'http://forensic_app:8000/fraud',
  '/api/risk': 'http://forensic_app:8000/risk',
  '/api/evidence': 'http://forensic_app:8000/evidence',
  '/api/reconciliation': 'http://forensic_app:8000/reconciliation',
  '/api/analytics': 'http://forensic_app:8000/analytics',
  '/api/monitoring': 'http://forensic_app:8000/monitoring',
  '/api/webhooks': 'http://forensic_app:8000/webhooks',
  '/api/upload': 'http://forensic_app:8000/upload',
  '/api/search': 'http://forensic_app:8000/search',
  '/api/export': 'http://forensic_app:8000/export',
  '/api/config': 'http://forensic_app:8000/config',
  '/api/audit': 'http://forensic_app:8000/audit',
};

const getServiceUrl = (path) => {
  const servicePath = Object.keys(services).find((key) => path.startsWith(key));
  return servicePath ? services[servicePath] : null;
};

module.exports = {
  getServiceUrl,
};
