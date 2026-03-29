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

    - Time: It uses the available time as the  maximum anything more is dropped.
    - Priority: The priority is used to order and determine tasks
    - Preference: Owner's preferred slots are considered first then the rest are filled. 

- How did you decide which constraints mattered most?

    Priority was considered the most important as it gives us the direct information on what the owners cares for most. The time is then next that is used for scheduling.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

    Because we give priority as the most important the prioprity one task of more time is given first even if there are 2 tasks or more that can be done in lesser time with low priority. 

- Why is that tradeoff reasonable for this scenario?

    It is reasonable because tasks like food and walking are mandotory and are to be done at the right time compared to secondary tasks. Thus priority seems to be the best option to order from.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

    I used AI for helping me to understand the code, write script for UML diagram, help with writng functions and test cases. I didn't use AI for debegging as much cause I had a really good plan from start.

- What kinds of prompts or questions were most helpful?

    I think prompts like "Help me to identify issues with code" is useful to find issues and prompts like "Help to solve thsi problem" are good to get code snippets.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

    The Ai was trying to add more tables in the planning phase where I had to suggest it to not make it complex unnessarily. 

- How did you evaluate or verify what the AI suggested?

    I tested all the work using tests and also manually checking some of the common cases uisng the UI.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

    - Recurrinf tasks
    - Sorting
    - Conflict detection
    - Schedule building
    - Filtering

- Why were these tests important?

    These are required to check if the scheduler works correctly as I designed and no task is being missed out. And to makes ure everything works as expected before they are published.

**b. Confidence**

- How confident are you that your scheduler works correctly?

    4/5

- What edge cases would you test next if you had more time?

    Maybe more tasks that focus on more niche edge cases like monthly recurrence and more.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I am pretty proud for this week's project as it came along a lot easier and I am satisfied with the result.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would probabily focus more on the UI aspects and find something new to enhance or extend the project's capabilities.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

I learned that they are really good in created UML diagram and for test cases. As writing the correct test cases will help to find issues and move faster.
