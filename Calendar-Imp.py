from datetime import datetime

# --- Refactoring: Replace Conditional with Polymorphism ---
class Event:
    """
    Represents a calendar event, with:
    - a title (string)
    - start_time/end_time (datetime)
    - description (string, optional)
    """
    def __init__(self, title, start_time, end_time, description=""):
        self.title = title
        self.start_time = start_time
        self.end_time = end_time
        self.description = description

    def update_event(self, title=None, start_time=None, end_time=None, description=None):
        """Updates any provided fields of the event."""
        if title is not None:
            self.title = title
        if start_time is not None:
            self.start_time = start_time
        if end_time is not None:
            self.end_time = end_time
        if description is not None:
            self.description = description

    def matches_title(self, title):
        return self.title == title  # CHANGED: Added for polymorphic title matching

    def __str__(self):
        return (f"Event(title='{self.title}', "
                f"start={self.start_time}, end={self.end_time}, "
                f"description='{self.description}')")


# --- Refactoring: Extract Class (Abstract Factory) ---
class EventFactory:  # CHANGED: Extracted class for event creation (Abstract Factory)
    def create_event(self, title, start_time, end_time, description=""):
        raise NotImplementedError

class DefaultEventFactory(EventFactory):  # CHANGED: Extracted class for event creation (Concrete implementation)
    def create_event(self, title, start_time, end_time, description=""):
        return Event(title, start_time, end_time, description)


class Calendar:
    """
    A calendar that holds multiple Event objects.
    User can add, remove, update events.
    """
    def __init__(self, name, event_factory=None):  # CHANGED: Added event_factory parameter
        self.name = name
        self.events = []
        self.event_factory = event_factory if event_factory is not None else DefaultEventFactory()  # CHANGED: Set default event factory

    def add_event(self, event):
        """Adds an Event object to the list."""
        self.events.append(event)

    def remove_event(self, event_title):
        """
        Removes an event from the calendar by matching its title.
        Returns True if an event was removed, False otherwise.
        """
        for i, evt in enumerate(self.events):
            if evt.matches_title(event_title):  # CHANGED: Use polymorphic matching
                del self.events[i]
                return True
        return False

    def update_event(self, event_title, **update_fields):
        """
        Finds an event by title and updates its fields (start_time, end_time, etc.).
        Returns True if found and updated, False otherwise.
        """
        for evt in self.events:
            if evt.matches_title(event_title):  # CHANGED: Use polymorphic matching
                evt.update_event(**update_fields)
                return True
        return False

    def __str__(self):
        return f"Calendar(name='{self.name}', events_count={len(self.events)})"


class User:
    """
    Each user has a username and a dictionary of calendars.
    """
    def __init__(self, username):
        self.username = username
        self.calendars = {}  # dict of name->Calendar

    def create_calendar(self, calendar_name):
        """
        Creates a new Calendar with the given name and stores it in the user's dictionary.
        Returns True if creation is successful, False if the name already exists.
        """
        if calendar_name in self.calendars:
            return False
        new_cal = self.factory_create_calendar(calendar_name)  # CHANGED: Using factory method
        self.calendars[calendar_name] = new_cal
        return True

    def factory_create_calendar(self, calendar_name):  # CHANGED: Factory Method implementation for Calendar creation
        return Calendar(calendar_name)

    def remove_calendar(self, calendar_name):
        """
        Deletes a calendar by name.
        Returns True if the calendar existed and was removed, False otherwise.
        """
        return self.calendars.pop(calendar_name, None) is not None

    def update_calendar_name(self, old_name, new_name):
        """
        Renames a calendar if possible.
        Returns True on success, False if old_name doesn't exist or new_name is taken.
        """
        if old_name not in self.calendars or new_name in self.calendars:
            return False
        cal = self.calendars.pop(old_name)
        cal.name = new_name
        self.calendars[new_name] = cal
        return True

    def __str__(self):
        return (f"User(username='{self.username}', "
                f"calendars_count={len(self.calendars)})")


class CalendarsApp:
    """
    High-level manager holding multiple users in memory.
    Allows creation/deletion of users, and access to specific users.
    """
    def __init__(self):
        self.users = {}  # dict of username->User

    def create_user(self, username):
        """Creates a new user, returns True on success, False if user already exists."""
        if username in self.users:
            return False
        self.users[username] = User(username)
        return True

    def get_user(self, username):
        """Returns the User object if it exists, or None otherwise."""
        return self.users.get(username)

    def delete_user(self, username):
        """Removes a user entirely from the system (all calendars and events are lost)."""
        return self.users.pop(username, None) is not None

    def list_users(self):
        """Returns a list of all usernames in the system."""
        return list(self.users.keys())


def main():
    """
    Command Line Interface:
      1) Storing and working with Gregorian calendar dates via datetime
      2) Distinct sets of events per calendar with start/end times
      3) CRUD on events (add/remove/update)
      4) Multiple users with multiple calendars
      5) CRUD on calendars (add/remove/update name)
    """
    app = CalendarsApp()

    while True:
        print("\n--- Main Menu ---")
        print("1) Create User")
        print("2) Switch to an Existing User")
        print("3) List All Users")
        print("4) Delete User")
        print("5) Exit")
        choice = input("Enter a choice: ").strip()

        if choice == "1":
            username = input("Enter a username: ").strip()
            if app.create_user(username):
                print(f"User '{username}' created successfully.")
            else:
                print(f"User '{username}' already exists.")
        elif choice == "2":
            username = input("Enter existing username: ").strip()
            user = app.get_user(username)
            if user:
                user_menu(user)
            else:
                print(f"No user '{username}' found.")
        elif choice == "3":
            users = app.list_users()
            if users:
                print("Current users:", ", ".join(users))
            else:
                print("No users in the system yet.")
        elif choice == "4":
            username = input("Enter username to delete: ").strip()
            if app.delete_user(username):
                print(f"User '{username}' deleted.")
            else:
                print(f"No user '{username}' found.")
        elif choice == "5":
            print("Exiting program. All data is lost.")
            break
        else:
            print("Invalid choice. Please try again.")


def user_menu(user):
    """
    Sub-menu for a specific user
    """
    while True:
        print(f"\n--- {user.username}'s Menu ---")
        print("1) Create a Calendar")
        print("2) Remove a Calendar")
        print("3) List Calendars and Events")
        print("4) Add Event to a Calendar")
        print("5) Remove Event from a Calendar")
        print("6) Update an Event")
        print("7) Rename a Calendar")
        print("8) Go Back")

        choice = input("Enter a choice: ").strip()
        if choice == "1":
            cal_name = input("Enter new calendar name: ").strip()
            if user.create_calendar(cal_name):
                print(f"Calendar '{cal_name}' created.")
            else:
                print(f"A calendar named '{cal_name}' already exists.")
        elif choice == "2":
            cal_name = input("Enter calendar name to remove: ").strip()
            if user.remove_calendar(cal_name):
                print(f"Calendar '{cal_name}' removed.")
            else:
                print(f"No calendar '{cal_name}' found.")
        elif choice == "3":
            if not user.calendars:
                print("No calendars available.")
            else:
                for cal in user.calendars.values():
                    print(f"Calendar: {cal.name} (events: {len(cal.events)})")
                    for evt in cal.events:
                        print(f"  - {evt.title}: {evt.start_time} to {evt.end_time}")
        elif choice == "4":
            cal_name = input("Enter calendar name: ").strip()
            calendar = user.calendars.get(cal_name)
            if not calendar:
                print(f"No calendar '{cal_name}' found.")
            else:
                title = input("Event title: ").strip()
                start_str = input("Start time (YYYY-MM-DD HH:MM): ").strip()
                end_str = input("End time (YYYY-MM-DD HH:MM): ").strip()
                description = input("Description: ").strip()
                try:
                    start_dt = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
                    end_dt = datetime.strptime(end_str, "%Y-%m-%d %H:%M")
                except ValueError:
                    print("Invalid date/time format. Please use YYYY-MM-DD HH:MM.")
                    continue
                # CHANGED: Using EventFactory (Abstract Factory) to create event
                new_event = calendar.event_factory.create_event(title, start_dt, end_dt, description)
                calendar.add_event(new_event)
                print(f"Event '{title}' added to calendar '{cal_name}'.")
        elif choice == "5":
            cal_name = input("Enter calendar name: ").strip()
            calendar = user.calendars.get(cal_name)
            if not calendar:
                print(f"No calendar '{cal_name}' found.")
            else:
                evt_title = input("Enter event title to remove: ").strip()
                if calendar.remove_event(evt_title):
                    print(f"Removed event '{evt_title}'.")
                else:
                    print(f"Event '{evt_title}' not found.")
        elif choice == "6":
            cal_name = input("Enter calendar name: ").strip()
            calendar = user.calendars.get(cal_name)
            if not calendar:
                print(f"No calendar '{cal_name}' found.")
            else:
                evt_title = input("Enter the event title to update: ").strip()
                new_title = input("New title (press enter to skip): ").strip()
                start_str = input("New start time YYYY-MM-DD HH:MM (enter to skip): ").strip()
                end_str = input("New end time YYYY-MM-DD HH:MM (enter to skip): ").strip()
                desc_str = input("New description (press enter to skip): ").strip()

                update_fields = {}
                if new_title:
                    update_fields["title"] = new_title
                if start_str:
                    try:
                        update_fields["start_time"] = datetime.strptime(start_str, "%Y-%m-%d %H:%M")
                    except ValueError:
                        print("Invalid start time format. Update skipped for start time.")
                if end_str:
                    try:
                        update_fields["end_time"] = datetime.strptime(end_str, "%Y-%m-%d %H:%M")
                    except ValueError:
                        print("Invalid end time format. Update skipped for end time.")
                if desc_str:
                    update_fields["description"] = desc_str

                if calendar.update_event(evt_title, **update_fields):
                    print(f"Event '{evt_title}' updated.")
                else:
                    print(f"No event '{evt_title}' found.")
        elif choice == "7":
            old_name = input("Enter current calendar name: ").strip()
            new_name = input("Enter new calendar name: ").strip()
            if user.update_calendar_name(old_name, new_name):
                print(f"Renamed '{old_name}' to '{new_name}'.")
            else:
                print("Rename failed. Check if the old name exists or the new name is already used.")
        elif choice == "8":
            # Go back to main menu
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main()
