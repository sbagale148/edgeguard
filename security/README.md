# EdgeGuard Security Documentation

Security stuff - threat models, assumptions, and how I'm trying to not get hacked. Coming in Milestone 3.

## What I Need to Document

- Threat model: What am I protecting? What could go wrong? How am I preventing it? What am I not preventing?
- Security features: Input validation, rate limiting, auth, proper error handling

## Security Features I'm Planning

- Input validation (people will send garbage)
- Rate limiting (prevent abuse of the abuse detection system - meta)
- Basic auth so random people can't just send events
- Error messages that don't leak info about the system

This is a learning project, so I'm not trying to make it Fort Knox, but I do want to learn proper security practices.

