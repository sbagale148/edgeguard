# EdgeGuard Development Log

Just writing down what I'm doing, why I'm doing it, and what I'm learning along the way. Probably more useful for future me than anyone else.

---

## Week 1-2: Setting Up the Foundation

**Goal:** Get the project structure in place before I start writing actual code

### What I Did

Set up the basic folder structure - frontend, backend, ml, security, docs. Created placeholder files so I know where things are supposed to go later. Also wrote a README that I'll probably rewrite a few times.

### Decisions I Made

**Folder structure:** Went with separate folders for each major component. Not sure if this is the "right" way, but it makes sense to me right now. I can always refactor later if it gets messy.

**Documentation:** Started this dev log because I know I'll forget why I made certain decisions in a few weeks. Also kept the proposal.txt at the root so I can reference it easily.

**Placeholder files:** Created minimal skeletons for frontend and backend. They don't do anything yet, but at least I know where the code is supposed to go.

### Tech Stack Decisions (Not Made Yet)

Still haven't decided on:
- Frontend: React? Vue? Or just vanilla JS to keep it simple?
- Backend: Python (Flask/FastAPI) or Node.js? Leaning toward Python because I'm more familiar with it, but we'll see.
- Database: No idea yet. Probably SQLite for simplicity, maybe PostgreSQL if I need something more robust.

I'm deferring these decisions until Milestone 2 when I actually need to start building. No point in overthinking it now.

### What I'm Learning

Starting with a clear structure actually helps me think about the system as a whole. Before I had folders set up, I was just thinking about it abstractly. Now I can see where pieces fit together.

Also, having a dev log from the start is already useful. I'm writing this a few days after setting things up, and I'm already forgetting some of the reasoning.

### Open Questions

- What do "events" actually look like in this system? Log entries? HTTP requests? Auth attempts? Need to figure this out before I can design the API.
- How much security is "enough" for a learning project? I don't want to over-engineer, but I also want to learn proper security practices.
- ML stuff is way down the road, but I'm already wondering if I should use a library or try to implement something from scratch. Probably library, but we'll see.

### Next Up

Milestone 2 is about building the actual backend. Need to:
1. Pick a tech stack (probably Python)
2. Design the API endpoints
3. Figure out what the data model looks like
4. Get basic ingestion working

Should be fun. Or frustrating. Probably both.
