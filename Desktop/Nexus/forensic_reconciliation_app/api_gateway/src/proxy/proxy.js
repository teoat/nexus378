const axios = require('axios');
const { getServiceUrl } = require('../services/serviceRegistry');

const proxy = async (req, res, next) => {
  const serviceUrl = getServiceUrl(req.originalUrl);

  if (!serviceUrl) {
    return res.status(404).json({ error: 'Service not found' });
  }

  try {
    const response = await axios({
      method: req.method,
      url: `${serviceUrl}${req.originalUrl.replace(/\/api/, '')}`,
      data: req.body,
        // Only forward necessary headers, excluding sensitive ones
        ...Object.fromEntries(
          Object.entries(req.headers).filter(
            ([key]) => !['host', 'authorization', 'cookie'].includes(key.toLowerCase())
          )
        ),
        'X-Forwarded-For': req.ip,
      },
    });

    res.status(response.status).json(response.data);
  } catch (error) {
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({ error: 'Proxy error' });
    }
  }
};

module.exports = {
  proxy,
};
