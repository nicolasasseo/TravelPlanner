# PostgreSQL Setup Guide

## Prerequisites

- PostgreSQL 17 installed
- Know your postgres password

---

## Step 1: Create .env file

Create `.env` in project root:

```env
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@localhost:5432/travel_planner"
NEXTAUTH_SECRET="generate-random-secret-here"
NEXTAUTH_URL="http://localhost:3000"
SERPAPI_API_KEY="your-key"
OPENAI_API_KEY="your-key"
```

**Replace:**

- `YOUR_PASSWORD` with your PostgreSQL password
- Add your API keys

---

## Step 2: Setup Database with Prisma (Recommended)

```bash
# This creates the database and all tables
npx prisma migrate dev --name init

# Generate Prisma Client (TypeScript types)
npx prisma generate

# Open Prisma Studio to view database (optional)
npx prisma studio
```

Done! ✅

---

## Alternative: Manual psql Setup

### 1. Create Database Manually

```bash
# Open psql
psql -U postgres

# Inside psql, run:
CREATE DATABASE travel_planner;
\q
```

### 2. Then run migrations

```bash
npx prisma migrate dev
```

---

## Useful Commands

### Prisma Commands

```bash
# View database in browser GUI
npx prisma studio

# Reset database (delete all data)
npx prisma migrate reset

# Create new migration after schema changes
npx prisma migrate dev --name your_migration_name

# Apply migrations to production
npx prisma migrate deploy

# Pull database schema into Prisma (reverse engineer)
npx prisma db pull

# Push schema to database without migrations
npx prisma db push
```

### psql Commands (inside psql session)

```sql
-- List databases
\l

-- Connect to database
\c travel_planner

-- List tables
\dt

-- Describe table
\d "User"
\d "Trip"

-- View data
SELECT * FROM "User";
SELECT * FROM "Trip";

-- Count records
SELECT COUNT(*) FROM "ChatMessage";

-- Quit
\q
```

---

## Common Issues & Solutions

### Issue: "database does not exist"

**Solution:**

```bash
npx prisma migrate dev
```

Prisma will create it automatically.

### Issue: "password authentication failed"

**Solution:** Check your `.env` file has the correct password.

### Issue: Port 5432 already in use

**Solution:** PostgreSQL is already running (good!). Just run migrations.

### Issue: Prisma Client outdated

**Solution:**

```bash
npx prisma generate
```

---

## What Each Command Does

| Command                    | What It Does                                          |
| -------------------------- | ----------------------------------------------------- |
| `npx prisma migrate dev`   | Creates database + runs migrations + generates client |
| `npx prisma studio`        | Opens GUI to view/edit data                           |
| `npx prisma migrate reset` | Deletes all data and recreates tables                 |
| `npx prisma generate`      | Generates TypeScript types                            |
| `npx prisma db push`       | Quick schema sync (dev only)                          |

---

## Your Next Steps

1. **Create `.env` file** with your PostgreSQL password
2. **Run:** `npx prisma migrate dev --name init`
3. **Run:** `npx prisma generate`
4. **Optional:** `npx prisma studio` (to view database)
5. **Start your app:** `npm run dev`

That's it! 🎉
