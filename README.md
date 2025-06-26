# Travel Planner

## Overview

Travel Planner is a full-stack web application that allows users to plan, visualize, and manage their travel itineraries. Users can create trips, add locations, and view their travel history on an interactive 3D globe.

---

## Tech Stack

- **Frontend:** Next.js (App Router, React 19, Tailwind CSS)
- **Backend:** Next.js API routes, NextAuth.js for authentication
- **Database:** PostgreSQL (via Prisma ORM)
- **3D Visualization:** react-globe.gl, three.js
- **Drag & Drop:** @dnd-kit
- **File Uploads:** uploadthing
- **UI Components:** Radix UI, Lucide Icons

---

## Features

- User authentication (NextAuth.js, Prisma)
- Create, edit, and delete trips
- Add and reorder locations within trips
- Visualize visited countries and locations on a 3D globe
- Responsive, modern UI

---

## Prerequisites

- **Node.js** (v18+ recommended)
- **npm** or **yarn**
- **PostgreSQL** installed and running on your PC

---

## Getting Started

### 1. Clone the repository

```bash
git clone <your-repo-url>
cd travel_planner
```

### 2. Install dependencies

```bash
npm install
# or
yarn install
```

### 3. Set up PostgreSQL locally

If you don't have PostgreSQL installed, you can download it from [the official website](https://www.postgresql.org/download/).

**Basic setup steps:**

1. Install PostgreSQL and follow the installer instructions.
2. During installation, set a password for the default `postgres` user.
3. After installation, open the SQL Shell (psql) or use a GUI tool like pgAdmin.
4. Create a new database for the project:
   ```sql
   CREATE DATABASE travel_planner;
   ```
5. (Optional) Create a dedicated user and grant privileges:
   ```sql
   CREATE USER travel_user WITH PASSWORD 'yourpassword';
   GRANT ALL PRIVILEGES ON DATABASE travel_planner TO travel_user;
   ```

### 4. Configure Environment Variables

Create a `.env` file in the root directory and add your PostgreSQL connection string:

```
DATABASE_URL="postgresql://<user>:<password>@localhost:5432/<database_name>"
NEXTAUTH_SECRET="your-random-secret"
NEXTAUTH_URL="http://localhost:3000"
```

Replace `<user>`, `<password>`, and `<database_name>` with your PostgreSQL credentials.

### 5. Set up the database

Run Prisma migrations to set up your database schema:

```bash
npx prisma migrate dev --name init
```

### 6. Start the development server

```bash
npm run dev
# or
yarn dev
```

Visit [http://localhost:3000](http://localhost:3000) in your browser.

---

## Useful Scripts

- `npm run dev` — Start the development server
- `npm run build` — Build for production
- `npm start` — Start the production server
- `npx prisma studio` — Open Prisma Studio to view/edit your database

---

## Project Structure

- `app/` — Next.js app directory (pages, API routes, components)
- `components/` — Reusable React components
- `lib/` — Utility functions and server-side logic
- `prisma/` — Prisma schema and migrations

---

## Notes

- The 3D globe visualization only works in the browser (not server-side).
- Make sure your PostgreSQL server is running before starting the app.
- For authentication, configure OAuth providers in `.env` as needed (see NextAuth.js docs).
