const Joi = require('joi');

const validate = (schema) => (req, res, next) => {
  const { error } = schema.validate({
    body: req.body,
    query: req.query,
    params: req.params,
  });

  if (error) {
    return res.status(400).json({
      error: 'Validation failed',
      details: error.details.map((detail) => detail.message),
    });
  }

  next();
};

module.exports = {
  validate,
};
