const Joi = require('joi');

const loginSchema = Joi.object({
  body: Joi.object({
    email: Joi.string().email().required(),
    password: Joi.string().min(6).required(),
  }),
  query: Joi.object(),
  params: Joi.object(),
});

module.exports = {
  loginSchema,
};
