import requests
import random
import uuid

BASE_URL = "http://localhost:8000"  # Change this if your API is running elsewhere
EVENT_ID = (
    "5f40798c-ed95-4b11-bcc3-5ab6b4a4badb"  # The event ID where users will be added
)

# Define some random names
NAMES = [
    "Alice",
    "Bob",
    "Charlie",
    "David",
    "Eve",
    "Frank",
    "Grace",
    "Hannah",
    "Ian",
    "Jack",
    "Kate",
    "Leo",
    "Mia",
    "Noah",
    "Olivia",
    "Paul",
    "Quinn",
    "Riley",
    "Sophia",
    "Tom",
    "Uma",
    "Victor",
    "Wendy",
    "Xander",
    "Yasmin",
    "Zane",
    "Abby",
    "Brian",
    "Cindy",
    "Derek",
    "Ella",
    "Finn",
    "Gina",
    "Henry",
    "Isla",
    "James",
    "Karen",
    "Liam",
    "Mila",
    "Nathan",
    "Oscar",
    "Penny",
    "Quincy",
    "Ron",
    "Sasha",
    "Theo",
    "Ursula",
    "Vincent",
    "Willow",
    "Xena",
]


# Function to create a user
def create_user(name, role):
    user_data = {
        "name": name,
        "email": f"{name.lower()}@example.com",
        "role": role,
        "profile": {
            "github": f"https://github.com/{name.lower()}",
            "skills": ["Python", "FastAPI"],
        },
    }
    response = requests.post(f"{BASE_URL}/users/", json=user_data)
    if response.status_code == 200:
        user_id = response.json()["id"]
        print(f"✅ Created {role}: {name} ({user_id})")
        return user_id
    else:
        print(f"❌ Failed to create {role}: {name} - {response.text}")
        return None


# Function to add a user to an event
def add_user_to_event(user_id, role):
    participant_data = {"user_id": user_id, "event_id": EVENT_ID, "role": role}
    response = requests.post(
        f"{BASE_URL}/events/{EVENT_ID}/participants", json=participant_data
    )
    if response.status_code == 200:
        print(f"🔗 Added {user_id} as {role} to event {EVENT_ID}")
    else:
        print(f"❌ Failed to add {user_id} to event - {response.text}")


# Create users and add them to the event
def main():
    all_users = []

    # Create 45 participants
    for i in range(2):
        name = random.choice(NAMES) + str(random.randint(1, 99))  # Ensure uniqueness
        user_id = create_user(name, "participant")
        if user_id:
            add_user_to_event(user_id, "participant")
            all_users.append(user_id)

    # Create 5 organizers
    for i in range(5):
        name = random.choice(NAMES) + str(random.randint(1, 99))  # Ensure uniqueness
        user_id = create_user(name, "organizer")
        if user_id:
            add_user_to_event(user_id, "organizer")
            all_users.append(user_id)

    print("\n🎉 All users created and added to the event successfully!")


if __name__ == "__main__":
    main()
