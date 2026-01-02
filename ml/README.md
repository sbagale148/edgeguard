# EdgeGuard ML / AI Layer

The part that tries to figure out if something weird is happening. This comes way later (Milestone 4), so it's just a placeholder for now.

## What I'm Thinking About

Probably going to start with simple statistical methods or basic ML algorithms. Not trying to build GPT here - just need to detect when something looks off.

Maybe some NLP stuff for analyzing log text, but that's optional. The main goal is detecting anomalies in the event data.

## My Approach

- Only use ML where it actually helps (not just because it's cool)
- Keep it simple and interpretable - I want to understand why it flagged something
- Document why I chose ML for each use case
- Actually evaluate if it works or if it's just flagging everything

The ML code will be separate from the main system logic so I can swap it out or improve it without breaking everything else.

