# EdgeGuard

Trying to figure out how companies like Cloudflare actually detect abuse and weird stuff happening at the edge. This is a semester project where I'm building a system that takes in logs and events, analyzes them for suspicious behavior, and shows what's going on through a dashboard.

## What This Is

EdgeGuard is basically me learning how to build a security monitoring system from scratch. It's got:
- A backend API that accepts events/logs
- Some ML stuff to detect anomalies (probably simple at first)
- A web dashboard to actually see what's happening
- Documentation about security assumptions and threats

**Important disclaimer:** This is a learning project. It's not production-ready, and I'm not trying to make it enterprise-grade. The goal is to understand how these systems work, make mistakes, and learn from them.

## Project Structure

```
EdgeGuard/
├── frontend/     # Dashboard (still figuring out React vs vanilla JS)
├── backend/      # API server (probably Python, maybe Node)
├── ml/           # Anomaly detection stuff
├── security/     # Threat models and security notes
└── docs/         # Dev logs and random thoughts
```

## Current Status

✅ **Milestone 1 done** - Got the project structure set up  
⏳ **Milestone 2** - Need to build the actual backend API  
⏳ **Milestone 3** - Add security features and threat modeling  
⏳ **Milestone 4** - Implement ML/anomaly detection  
⏳ **Milestone 5** - Build the dashboard  
⏳ **Milestone 6** - Clean everything up and document what I learned  

## What I'm Trying to Learn

- How to design a system that actually evolves over time (not just a one-off script)
- Applying security principles in real code, not just theory
- Using ML where it makes sense, not just because it's cool
- Writing code that gets better through iteration
- Actually documenting why I made decisions (and when I messed up)

## Getting Started

Haven't figured out the tech stack yet, so installation instructions are coming later. Check back after Milestone 2.

## Development Log

I'm keeping a dev log at [docs/dev_log.md](docs/dev_log.md) where I write down decisions, mistakes, and random thoughts as I go. It's probably more honest than this README.

## More Details

See [proposal.txt](proposal.txt) for the full project proposal with all the details about milestones and timeline.

