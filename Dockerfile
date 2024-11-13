# Step 1: Build the Vite app
FROM node:16 AS build

# Set the working directory to /app/frontend
WORKDIR /app/frontend

# Install dependencies
COPY frontend/package.json frontend/package-lock.json ./
RUN npm install

# Copy the source code
COPY frontend ./

# Step 2: Run the Vite app in development mode
CMD ["npm", "run", "dev", "--", "--host"]

# Expose the port where the Vite development server will run
EXPOSE 80
