# PawPal+ Project Reflection

## 1. System Design

**Core actions**
Three core actions that the user should be able to perform 3 core actions:
- Add a pet
- See current tasks/schedule for the day
- Add care tasks for a pet (with duration and priority


**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

For the initial design for the UML, I had a total of 4 classes; scheduler, owner, pet, and task in that hierarchy order I listed them out. An Owner has one or more Pets, each Pet has its own list of Tasks, and the Scheduler works from the Owner to build a daily plan. I kept data and logic separate: the first three classes mostly hold information, and the Scheduler holds the planning logic, which makes it easier to test.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

The original design was a bit more complicated as it had more information relating to what the pet was such as its breed. However this was changed as it added unnecessary complexity to the design.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My scheduler places tasks greedily by priority, from high to low, back to back starting at the owner’s day start, and skips any task that doesn’t fit in the remaining time. A task’s preferred time only breaks ties within the same priority, so a task the owner wants at 08:00 might land at 08:10, and overlapping preferred times produce a warning rather than a rearranged plan. I think this is reasonable for a busy pet owner because it guarantees that critical tasks like feeding and medication always make it into the day. Honoring exact times would mean handling gaps, deciding which task moves when two clash, and dealing with time slots that have already passed, which would make the logic much harder to understand and test. Flagging conflicts instead of resolving them keeps the scheduler predictable and leaves the final call to the owner, who knows their day better than the app does.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
