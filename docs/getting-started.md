# Getting Started Tutorial

A hands-on tutorial to get you up and running with Python Super Heroes in under 10 minutes.

## What You'll Build

By the end of this tutorial, you'll have:

- ✅ A running microservices system with 4 services and 4 databases
- ✅ Created your first superhero fight
- ✅ Understood the system architecture
- ✅ Run performance tests

**Time Required**: 10 minutes

## Prerequisites

You'll need:

- **Docker** & **Docker Compose** installed ([Install Guide](https://docs.docker.com/get-docker/))
- **curl** or a web browser
- **(Optional)** **jq** for pretty JSON output

**Check your installation**:
``````bash
docker --version
# Should show: Docker version 20.x.x or higher

docker-compose --version
# Should show: Docker Compose version 2.x.x or higher
``````

## Step 1: Get the Code

Clone the repository:

``````bash
git clone https://github.com/flyaruu/python-super-heroes.git
cd python-super-heroes
``````

**What you should see**:
``````
python-super-heroes/
├── services/
├── database/
├── k6/
├── compose.yml
└── README.md
``````

## Step 2: Start the System

Start all services with one command:

``````bash
docker-compose up -d
``````

**What's happening**:
- Docker pulls images for PostgreSQL, MariaDB, MongoDB
- Builds custom images for each Python service
- Initializes databases with hero, villain, and location data
- Starts 4 microservices on different ports

**Expected output**:
``````
Creating network "python-super-heroes_default" ... done
Creating python-super-heroes_heroes-db_1    ... done
Creating python-super-heroes_villains-db_1  ... done
Creating python-super-heroes_locations-db_1 ... done
Creating python-super-heroes_fights-db_1    ... done
Creating python-super-heroes_heroes_1       ... done
Creating python-super-heroes_villains_1     ... done
Creating python-super-heroes_locations_1    ... done
Creating python-super-heroes_fights_1       ... done
``````

**Verify all services are running**:
``````bash
docker-compose ps
``````

You should see all services with status "Up":
``````
NAME                STATUS    PORTS
heroes-db           Up        0.0.0.0:5432->5432/tcp
villains-db         Up        0.0.0.0:5433->5432/tcp
locations-db        Up        0.0.0.0:3306->3306/tcp
fights-db           Up        0.0.0.0:27017->27017/tcp
heroes              Up        0.0.0.0:8001->8000/tcp
villains            Up        0.0.0.0:8002->8000/tcp
locations           Up        0.0.0.0:8003->8000/tcp
fights              Up        0.0.0.0:8004->8000/tcp
``````

**⏱️ Time Check**: ~2 minutes

## Step 3: Explore Heroes

Let's fetch all heroes from the database:

``````bash
curl http://localhost:8001/api/heroes | jq
``````

**Sample output**:
``````json
[
  {
    "id": 1,
    "name": "Chewbacca",
    "otherName": "",
    "level": 30,
    "picture": "https://raw.githubusercontent.com/.../chewbacca.jpg",
    "powers": "Super Strength, Agility, Animal Attributes, Jaw Strength..."
  },
  {
    "id": 51,
    "name": "Yoda",
    "otherName": "",
    "level": 286000,
    "picture": "https://raw.githubusercontent.com/.../yoda.jpg",
    "powers": "Acrobatics, Agility, Telekinesis, The Force..."
  }
]
``````

**Get a random hero**:
``````bash
curl http://localhost:8001/api/heroes/random_hero | jq
``````

**Try it in your browser**: Open [http://localhost:8001/api/heroes](http://localhost:8001/api/heroes)

**⏱️ Time Check**: ~3 minutes

## Step 4: Explore Villains

Fetch all villains:

``````bash
curl http://localhost:8002/api/villains | jq
``````

**Get a random villain**:
``````bash
curl http://localhost:8002/api/villains/random_villain | jq
``````

**Example villain**:
``````json
{
  "id": 101,
  "name": "Lex Luthor",
  "otherName": "Alexander Luthor",
  "level": 85,
  "picture": "https://raw.githubusercontent.com/.../lexluthor.jpg",
  "powers": "Genius Intellect, Powered Armor"
}
``````

## Step 5: Explore Locations

Fetch fight locations:

``````bash
curl http://localhost:8003/api/locations | jq
``````

**Get a random location**:
``````bash
curl http://localhost:8003/api/locations/random_location | jq
``````

**Example location**:
``````json
{
  "id": 1,
  "name": "Gotham City",
  "description": "An American city rife with corruption and crime...",
  "picture": "https://raw.githubusercontent.com/.../gotham_city.jpg",
  "type": "CITY"
}
``````

**⏱️ Time Check**: ~5 minutes

## Step 6: Execute Your First Fight!

Now for the exciting part - let's make a hero and villain fight!

**Automatic fight** (easiest):
``````bash
curl http://localhost:8004/api/fights/execute_fight | jq
``````

**Sample output**:
``````json
{
  "fightId": "550e8400-e29b-41d4-a716-446655440000",
  "hero": {
    "id": 5,
    "name": "Batman",
    "level": 87
  },
  "villain": {
    "id": 23,
    "name": "The Joker",
    "level": 65
  },
  "location": {
    "id": 1,
    "name": "Gotham City",
    "type": "CITY"
  },
  "winner": "hero",
  "winnerName": "Batman",
  "fightDate": "2026-02-13T13:38:00Z"
}
``````

**How fights work**: The character with the **higher level wins**!

**⏱️ Time Check**: ~6 minutes

## Step 7: Manual Fight Selection

Want to choose specific fighters? Let's do it step by step:

**1. Get random fighters**:
``````bash
curl http://localhost:8004/api/fights/randomfighters | jq
``````

**Output**:
``````json
{
  "hero": {
    "id": 1,
    "name": "Superman",
    "level": 95,
    "powers": "Flight, Super Strength, Heat Vision"
  },
  "villain": {
    "id": 2,
    "name": "Lex Luthor",
    "level": 85,
    "powers": "Genius Intellect, Powered Armor"
  }
}
``````

**2. Get random location**:
``````bash
curl http://localhost:8004/api/fights/randomlocation | jq
``````

**3. Execute the fight**:
``````bash
curl -X POST http://localhost:8004/api/fights \
  -H "Content-Type: application/json" \
  -d '{
    "hero": {
      "id": 1,
      "name": "Superman",
      "level": 95,
      "powers": "Flight, Super Strength"
    },
    "villain": {
      "id": 2,
      "name": "Lex Luthor",
      "level": 85,
      "powers": "Genius Intellect"
    },
    "location": {
      "id": 1,
      "name": "Metropolis",
      "type": "CITY"
    }
  }' | jq
``````

**⏱️ Time Check**: ~8 minutes

## Step 8: Interactive API Docs

FastAPI provides automatic interactive documentation!

**Open in your browser**:

- **Heroes Service**: [http://localhost:8001/docs](http://localhost:8001/docs)
- **Villains Service**: [http://localhost:8002/docs](http://localhost:8002/docs)
- **Locations Service**: [http://localhost:8003/docs](http://localhost:8003/docs)
- **Fights Service**: [http://localhost:8004/docs](http://localhost:8004/docs)

**Try it**:
1. Click on any endpoint
2. Click "Try it out"
3. Click "Execute"
4. See the response!

## Step 9: Run a Load Test

Let's see how the system performs under load:

``````bash
docker-compose run k6
``````

**What's happening**:
- k6 simulates 500 requests/second
- Tests fight execution under realistic load
- Validates performance thresholds

**Expected output**:
``````
✓ random fighters status is 200
✓ hero is not fallback
✓ villain is not fallback
✓ fight result is 200

checks.........................: 100.00%
http_req_duration..............: avg=125ms  p(95)=285ms
http_req_failed................: 0.00%
iterations.....................: 15000
``````

**⏱️ Time Check**: ~10 minutes

## Step 10: View Logs

Check what's happening inside the services:

``````bash
# View all logs
docker-compose logs -f

# View specific service
docker-compose logs -f fights

# View last 50 lines
docker-compose logs --tail=50 heroes
``````

## Step 11: Stop the System

When you're done:

``````bash
docker-compose down
``````

**To remove everything including data**:
``````bash
docker-compose down -v
``````

## Understanding the Architecture

You just ran a **microservices architecture** with:

``````
┌─────────────┐
│   Fights    │ ← Orchestrator (port 8004)
│   Service   │
└──────┬──────┘
       │ Calls these services:
   ┌───┴────┬─────────┬──────────┐
   │        │         │          │
┌──▼──┐  ┌─▼───┐  ┌──▼────┐  ┌──▼───┐
│Heroes│  │Vill-│  │Loca-  │  │Fights│
│ :8001│  │ains │  │tions  │  │  DB  │
│      │  │:8002│  │:8003  │  │MongoDB
└──┬───┘  └──┬──┘  └───┬───┘  └──────┘
   │         │         │
┌──▼──┐  ┌──▼──┐  ┌───▼────┐
│Postgres│ │Postgres│ │MariaDB │
└───────┘ └───────┘ └────────┘
``````

**Key Concepts**:

1. **Microservices**: Each service is independent
2. **Polyglot Persistence**: Different databases for different needs
3. **Service Orchestration**: Fights service calls others
4. **API Composition**: Aggregates data from multiple sources

## What's Next?

Now that you have the basics, explore:

1. **[API Reference](api-reference.md)**: Complete API documentation
2. **[Architecture Guide](architecture.md)**: Deep dive into system design
3. **[Development Guide](development.md)**: Start contributing
4. **[Load Testing Guide](load-testing.md)**: Advanced performance testing

## Troubleshooting

### Services won't start

``````bash
# Check Docker is running
docker ps

# View error logs
docker-compose logs

# Restart fresh
docker-compose down -v
docker-compose up -d
``````

### Can't connect to services

``````bash
# Check services are up
docker-compose ps

# Wait for databases to initialize (30 seconds)
sleep 30

# Test connectivity
curl http://localhost:8001/api/heroes
``````

### Port conflicts

If ports 8001-8004 are in use, edit `compose.yml`:

``````yaml
ports:
  - "9001:8000"  # Change 8001 to 9001
``````

### Database connection errors

``````bash
# Wait for health checks
docker-compose ps

# Restart specific service
docker-compose restart heroes

# Check database logs
docker-compose logs heroes-db
``````

## Questions?

- **Documentation**: Check the `docs/` folder
- **Issues**: [GitHub Issues](https://github.com/flyaruu/python-super-heroes/issues)
- **Discussions**: [GitHub Discussions](https://github.com/flyaruu/python-super-heroes/discussions)

## Congratulations! 🎉

You've successfully:
- ✅ Started a complete microservices system
- ✅ Explored all four services
- ✅ Executed superhero fights
- ✅ Run performance tests
- ✅ Understood the architecture

Ready to dive deeper? Check out the [Development Guide](development.md)!
