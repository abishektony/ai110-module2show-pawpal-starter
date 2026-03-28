# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

    1. Owner/pet info: The user should be able to enter their and their pet's information like time and preference.
    2. Add/edit pet care tasks: The suer should be able to add, remove nd edit the task according to their liking. 
    3. Generate a daily schedule: The user should be able to use the data he entered to generate a daily plan on the constraints

- Briefly describe your initial UML design.
    
    The design consists of 5 classes. An owner holds time constraits and has one or more pets. Each pet has their your set of tasks. The scheduler takes a owner and pet to create a dailyplan as output.

- What classes did you include, and what responsibilities did you assign to each?

  * Owner: Stores the name, time, preferences and has one or more pets
  * Pet: Stores the name, species and all the tasks
  * Task: Has a single task with name, duration, priority and optional time of dat
  * Scheduler: Has pets and owner times and schedules things accordingly.
  * DailyPlan: is the output object holds schedules and skipped tasks, total time used and reasoning behind it.

**b. Design changes**

- Did your design change during implementation?

    yes

- If yes, describe at least one change and why you made it.

    I did not think about seperating the dailyplan from schedular as it helps to keep things more organized

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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
