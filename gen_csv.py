import csv
import random
from datetime import datetime

# Start from where you left off (last admission was 119999)
start_admission = 120000
num_records = 100000  # 100,000 records

print(f"🚀 Starting generation of {num_records:,} records...")
print(f"📊 Admission numbers: {start_admission:,} to {start_admission + num_records - 1:,}")
print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("-" * 60)

# Sample first names and last names
first_names = [
    'James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer', 'Michael', 'Linda',
    'William', 'Elizabeth', 'David', 'Barbara', 'Richard', 'Susan', 'Joseph', 'Jessica',
    'Thomas', 'Sarah', 'Charles', 'Karen', 'Christopher', 'Nancy', 'Daniel', 'Lisa',
    'Matthew', 'Betty', 'Anthony', 'Helen', 'Mark', 'Sandra', 'Donald', 'Donna',
    'Steven', 'Carol', 'Paul', 'Ruth', 'Andrew', 'Sharon', 'Joshua', 'Michelle',
    'Kenneth', 'Laura', 'Kevin', 'Kimberly', 'Brian', 'Deborah', 'George', 'Emily',
    'Timothy', 'Amanda', 'Ronald', 'Melissa', 'Edward', 'Stephanie', 'Jason', 'Rebecca',
    'Jeffrey', 'Amy', 'Ryan', 'Angela', 'Jacob', 'Brenda', 'Gary', 'Nicole',
    'Nicholas', 'Anna', 'Eric', 'Samantha', 'Jonathan', 'Katherine', 'Stephen', 'Christine',
    'Larry', 'Kathleen', 'Justin', 'Rachel', 'Scott', 'Carolyn', 'Brandon', 'Janet',
    'Benjamin', 'Catherine', 'Samuel', 'Maria', 'Raymond', 'Heather', 'Gregory', 'Diane',
    'Frank', 'Olivia', 'Patrick', 'Joyce', 'Alexander', 'Julie', 'Jack', 'Virginia',
    'Dennis', 'Megan', 'Jerry', 'Victoria', 'Tyler', 'Frances', 'Aaron', 'Joan',
    'Jose', 'Katherine', 'Nathan', 'Megan', 'Ivan', 'Francis', 'Edwin', 'Florence',
    'Simon', 'Grace', 'Peter', 'Alice', 'George', 'Hannah', 'Victor', 'Rose',
    'Kenneth', 'Harriet', 'Samuel', 'Edith', 'Paul', 'Gloria', 'John', 'Agnes',
    'Thomas', 'Martha', 'Daniel', 'Irene', 'Michael', 'Janet', 'Robert', 'Joyce',
    'David', 'Catherine', 'James', 'Ruth', 'William', 'Margaret', 'Joseph', 'Helen',
    'Charles', 'Dorothy', 'Christopher', 'Betty', 'Anthony', 'Nancy', 'Mark', 'Sandra',
    'Donald', 'Carol', 'Steven', 'Sharon', 'Andrew', 'Michelle', 'Joshua', 'Laura',
    'Kenneth', 'Kimberly', 'Kevin', 'Deborah', 'Brian', 'Emily', 'George', 'Amanda',
    'Timothy', 'Melissa', 'Ronald', 'Stephanie', 'Edward', 'Rebecca', 'Jason', 'Amy',
    'Jeffrey', 'Angela', 'Ryan', 'Pamela', 'Jacob', 'Brenda', 'Gary', 'Nicole',
    'Nicholas', 'Anna', 'Eric', 'Samantha', 'Jonathan', 'Katherine', 'Stephen', 'Christine',
    'Larry', 'Kathleen', 'Justin', 'Rachel', 'Scott', 'Carolyn', 'Brandon', 'Janet',
    'Benjamin', 'Catherine', 'Samuel', 'Maria', 'Raymond', 'Heather', 'Gregory', 'Diane',
    'Frank', 'Olivia', 'Patrick', 'Joyce', 'Alexander', 'Julie', 'Jack', 'Virginia',
    'Dennis', 'Megan', 'Jerry', 'Victoria', 'Tyler', 'Frances', 'Aaron', 'Joan',
    'Jose', 'Katherine', 'Nathan', 'Megan', 'Ivan', 'Francis', 'Edwin', 'Florence',
    'Simon', 'Grace', 'Peter', 'Alice', 'George', 'Hannah', 'Victor', 'Rose',
    'Kenneth', 'Harriet', 'Samuel', 'Edith', 'Paul', 'Gloria', 'John', 'Agnes',
    'Thomas', 'Martha', 'Daniel', 'Irene', 'Michael', 'Janet', 'Robert', 'Joyce',
    'David', 'Catherine', 'James', 'Ruth', 'William', 'Margaret', 'Joseph', 'Helen',
    'Charles', 'Dorothy', 'Christopher', 'Betty', 'Anthony', 'Nancy', 'Mark', 'Sandra',
    'Donald', 'Carol', 'Steven', 'Sharon', 'Andrew', 'Michelle', 'Joshua', 'Laura'
]

last_names = [
    'Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis',
    'Rodriguez', 'Martinez', 'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson',
    'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin', 'Lee', 'Perez', 'Thompson',
    'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson', 'Walker',
    'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill',
    'Flores', 'Green', 'Adams', 'Nelson', 'Baker', 'Hall', 'Rivera', 'Campbell',
    'Mitchell', 'Carter', 'Roberts', 'Turner', 'Phillips', 'Evans', 'Collins', 'Edwards',
    'Stewart', 'Morris', 'Murphy', 'Cook', 'Rogers', 'Morgan', 'Peterson', 'Cooper',
    'Reed', 'Bailey', 'Bell', 'Howard', 'Ward', 'Cox', 'Diaz', 'Richardson',
    'Wood', 'Watson', 'Brooks', 'Bennett', 'Gray', 'James', 'Reyes', 'Cruz',
    'Hughes', 'Price', 'Myers', 'Long', 'Foster', 'Sanders', 'Ross', 'Powell',
    'Sullivan', 'Russell', 'Ortiz', 'Jenkins', 'Perry', 'Butler', 'Barnes', 'Fisher',
    'Henderson', 'Coleman', 'Simmons', 'Patterson', 'Jordan', 'Reynolds', 'Hamilton',
    'Graham', 'Kim', 'Gonzales', 'Alexander', 'Ramsey', 'Marshall', 'Olson', 'Rice',
    'Fox', 'Owens', 'Grant', 'Bryant', 'Mason', 'Kennedy', 'Chavez', 'Hansen',
    'Harrison', 'Hawkins', 'Daniels', 'Day', 'Bishop', 'Parker', 'Crawford', 'Owen',
    'McDonald', 'Daniel', 'Elliott', 'Carpenter', 'Hicks', 'Carr', 'Stone', 'Gomez',
    'Peters', 'Murray', 'Woods', 'Dixon', 'Schmidt', 'Wheeler', 'Ferguson', 'Wells',
    'Williamson', 'Webb', 'Tucker', 'Freeman', 'Hunt', 'Fuller', 'Owens', 'Cole',
    'Holland', 'Black', 'Burns', 'Ford', 'Pierce', 'Gray', 'Dean', 'Chapman',
    'Rodrigues', 'Silva', 'Santos', 'Costa', 'Pereira', 'Carvalho', 'Almeida', 'Nunes',
    'Oliver', 'Pena', 'Fields', 'Meyer', 'Medina', 'Kennedy', 'Howell', 'Jordan',
    'Davis', 'Allen', 'Ward', 'Ross', 'Mills', 'Adams', 'Johnston', 'Graham',
    'Spencer', 'Weaver', 'Wagner', 'Burke', 'Barker', 'Hoffman', 'Ross', 'Hayes',
    'Gibson', 'Burke', 'Bowers', 'Robinson', 'Alexander', 'Phillips', 'Campbell',
    'Harrison', 'Parker', 'Stevens', 'Roberts', 'Rogers', 'Cook', 'Morgan', 'Peterson',
    'Cooper', 'Reed', 'Bailey', 'Bell', 'Howard', 'Ward', 'Cox', 'Diaz',
    'Richardson', 'Wood', 'Watson', 'Brooks', 'Bennett', 'Gray', 'James', 'Reyes',
    'Cruz', 'Hughes', 'Price', 'Myers', 'Long', 'Foster', 'Sanders', 'Ross',
    'Powell', 'Sullivan', 'Russell', 'Ortiz', 'Jenkins', 'Perry', 'Butler', 'Barnes',
    'Fisher', 'Henderson', 'Coleman', 'Simmons', 'Patterson', 'Jordan', 'Reynolds',
    'Hamilton', 'Graham', 'Kim', 'Gonzales', 'Alexander', 'Ramsey', 'Marshall', 'Olson',
    'Rice', 'Fox', 'Owens', 'Grant', 'Bryant', 'Mason', 'Kennedy', 'Chavez',
    'Hansen', 'Harrison', 'Hawkins', 'Daniels', 'Day', 'Bishop', 'Parker', 'Crawford',
    'Owen', 'McDonald', 'Daniel', 'Elliott', 'Carpenter', 'Hicks', 'Carr', 'Stone',
    'Gomez', 'Peters', 'Murray', 'Woods', 'Dixon', 'Schmidt', 'Wheeler', 'Ferguson',
    'Wells', 'Williamson', 'Webb', 'Tucker', 'Freeman', 'Hunt', 'Fuller', 'Cole',
    'Holland', 'Black', 'Burns', 'Ford', 'Pierce', 'Gray', 'Dean', 'Chapman',
    'Ndegwa', 'Kamau', 'Ochieng', 'Wanjiru', 'Njeri', 'Wambui', 'Mwangi', 'Kimani',
    'Muthoni', 'Omondi', 'Otieno', 'Kariuki', 'Chege', 'Kiprop', 'Kipchoge', 'Muturi',
    'Ogolla', 'Owuor', 'Achieng', 'Adhiambo', 'Akwero', 'Amondi', 'Anindo', 'Awino',
    'Kiprop', 'Koech', 'Kosgey', 'Lagat', 'Langat', 'Maiyo', 'Mutai', 'Ng\'eno',
    'Kiptoo', 'Kipyego', 'Kiprotich', 'Cheruiyot', 'Kipkorir', 'Kibet', 'Kipchumba',
    'Chebet', 'Chepkorir', 'Cherop', 'Chemutai', 'Cheptoo', 'Kemboi', 'Kiprop', 'Kipngetich'
]

# Domains for email
domains = ['school.ac.ke', 'college.ac.ke', 'uni.ac.ke', 'students.ac.ke', 'academy.ac.ke']

filename = 'kuravote_100k_from120000.csv'

print(f"💾 Output file: {filename}")
print("-" * 60)

# Generate data
data = []
for i in range(num_records):
    admission = start_admission + i
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    domain = random.choice(domains)
    email = f"{first_name.lower()}.{last_name.lower()}{admission}@{domain}"
    data.append([admission, first_name, last_name, email])
    
    # Progress indicator
    if (i + 1) % 10000 == 0:
        print(f"✅ Generated {i + 1:,} records...")

# Write to CSV file
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['admission_number', 'first_name', 'last_name', 'email'])
    writer.writerows(data)

print("-" * 60)
print(f"✅ COMPLETED at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"📊 Total records: {num_records:,}")
print(f"📊 Admission range: {start_admission:,} to {start_admission + num_records - 1:,}")
print(f"💾 Output file: {filename}")

# Calculate file size
import os
if os.path.exists(filename):
    size_bytes = os.path.getsize(filename)
    size_mb = size_bytes / (1024 * 1024)
    print(f"📦 File size: {size_mb:.2f} MB")