classDiagram
    class Owner {
        +String name
        +int available_minutes
        +List~String~ preferences
        +List~Pet~ pets
        +add_pet(pet: Pet)
        +get_constraints() dict
    }

    class Pet {
        +String name
        +String species
        +List~Task~ tasks
        +add_task(task: Task)
        +remove_task(task_name: String)
        +get_tasks_by_priority() List~Task~
    }

    class Task {
        +String name
        +int duration_minutes
        +int priority
        +String preferred_time
        +String time
        +bool is_required
        +bool completed
        +String recurrence
        +mark_complete()
        +__repr__() String
    }

    class Scheduler {
        +Owner owner
        +Pet pet
        +schedule() DailyPlan
        +fits_in_time(tasks: List~Task~) bool
        +explain_plan(plan: DailyPlan) String
        +detect_conflicts(tasks: List~Task~) List~String~
        +complete_task(task: Task) Task
        +sort_by_time(tasks: List~Task~) List~Task~
        +filter_tasks(tasks: List~Task~, completed: bool, pet_name: String) List~Task~
        -_sort_by_priority(tasks: List~Task~) List~Task~
        -_filter_by_time(tasks: List~Task~) List~Task~
    }

    class DailyPlan {
        +List~Task~ scheduled_tasks
        +List~Task~ skipped_tasks
        +int total_minutes
        +String reasoning
        +display() String
    }

    Owner "1" *-- "0..*" Pet : owns
    Pet "1" *-- "0..*" Task : has
    Scheduler --> Owner : uses
    Scheduler --> Pet : uses
    Scheduler ..> DailyPlan : creates
