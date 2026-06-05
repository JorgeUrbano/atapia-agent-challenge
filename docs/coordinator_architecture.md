# Coordinator Agent Architecture

## Objective

The Coordinator Agent is the single entry point of the system.

It is responsible for receiving the user message, creating an execution plan, delegating work to specialized agents, and assembling the final response.

The Coordinator does not perform emotional analysis, safety assessment, or guidance generation directly.

Those responsibilities belong to specialized subagents.

---

## Architecture

User Message

↓

Coordinator Agent

↓

Execution Plan

↓

Subagent Delegation

↓

Response Assembly

↓

Final User Response

---

## Subagents

### Emotional Agent

Responsibilities:

* Detect emotional state
* Reflect emotional content
* Provide emotional validation

Outputs:

* Emotional analysis
* Emotional support response

---

### Safety Agent

Responsibilities:

* Assess potential safety concerns
* Detect crisis indicators
* Recommend safety actions when necessary

Outputs:

* Risk level
* Main concern
* Recommended action

---

### Guidance Agent

Responsibilities:

* Suggest practical next steps
* Encourage reflection
* Provide coping strategies

Outputs:

* Guidance summary
* Suggested next steps
* Follow-up question

---

## Coordinator Workflow

### Step 1: Receive User Message

The Coordinator receives the user's input.

### Step 2: Create Execution Plan

The Coordinator determines which specialist agents are required.

Current execution plan:

* Safety Agent
* Emotional Agent
* Guidance Agent

Future versions may selectively activate agents.

### Step 3: Delegate Tasks

The Coordinator transfers the request to the required subagents.

### Step 4: Aggregate Results

The Coordinator collects outputs from all participating agents.

### Step 5: Response Assembly

The Coordinator synthesizes a coherent final response.

The user should experience a single conversation with the Coordinator.

Internal planning and delegation should never be exposed.

---

## Future Extensions

### Memory Service

The Memory Service will provide:

* Conversation summaries
* Recurring themes
* Emotional history

The Memory Service is not an agent.

The Coordinator will query memory before delegation.

### Evaluation

Agent outputs will be evaluated using structured evaluation datasets.

### Observability

Execution plans, delegations, and agent outputs will be logged for monitoring and debugging.
