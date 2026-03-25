from app.database import collection




from pymongo import MongoClient

def run_cli_app():
    

    while True:
        print("\n1. Insert Data\n2. Show Data\n3. Find Operations\n4. Exit")
        num = int(input("Enter operation: "))

        if num == 1:
            name = input("Enter name: ")
            age = int(input("Enter age: "))
            role = input("Enter role: ")

            collection.insert_one({
                "name": name,
                "age": age,
                "role": role
            })
            print("✅ Data inserted successfully!")

        elif num == 2:
            print("\n📄 All Users:")
            for doc in collection.find():
                print(doc)

        elif num == 3:
            while True:
                print("\n1. Find age > value\n2. Find by name\n3. Find by role\n4. Back")
                choice = int(input("Enter find operation: "))

                if choice == 1:
                    age = int(input("Enter age: "))
                    for doc in collection.find({"age": {"$gt": age}}):
                        print(doc)

                elif choice == 2:
                    name = input("Enter name: ")
                    for doc in collection.find({"name": name}):
                        print(doc)

                elif choice == 3:
                    role = input("Enter role: ")
                    for doc in collection.find({"role": role}):
                        print(doc)

                elif choice == 4:
                    break

                else:
                    print("❌ Invalid choice")

        elif num == 4:
            print("👋 Exiting...")
            break

        else:
            print("❌ Invalid choice")



