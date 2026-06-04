# FlowEngineforMinds

We’ve created a brand‑new way to orchestrate multi‑agent workflows.

It’s a language for scripting multi‑agent plays. The backend compiler is open‑source and easy to port. If you want to run the workflows you design inside any system you’ve built yourself, it’s incredibly convenient.

The syntax natively supports branching, sequential execution, while loops, for loops, parallel execution (par), and if‑conditionals.

The syntax is simple. You can write a simplified version of “Stanford Town” in very few lines of code – set up 6 AI agents, 3 locations, and let them interact freely.

You might ask: “Simple or not, I still have to learn it, and I just don’t want to.” That’s fine – we also have a frontend (coming soon) that lets you generate the workflow you want with zero code. Then you can copy the script, take it away, and run it on your own backend software.

Right now everyone designs processes inside Agent Harnesses to constrain LLM behaviour, but a Harness is rigid, while FEM is alive. After you write a Harness, if you want to change the process, you often need to change a lot of code. With FEM, to change the process, you only need one click. You can also create all kinds of different processes.

The backend supports concurrency through asyncio, thread pools, and process pools – it handles multi‑threaded concurrency smoothly.

The Scope concept lets you isolate contextual perspectives with a single line of code. In every previous workflow orchestration tool, isolating each agent’s context required writing a lot of code. Here, it only takes one line.

You can seamlessly embed human interaction and Python modules. Your workflows don’t have to contain only AI agents.

If you want to embed the backend compiler into your own system, we’ve left very convenient interfaces. Just plug in your own memory module, context module, and LLM module, and FEM will run seamlessly inside your system.

When you want to modify a workflow, you just edit the FEM script. Leave everything else to the FEM compiler 💪

You can also package and distribute the FEM scripts you create, or take scripts shared by others and use them directly.
