# Base image
FROM node:16.13.1

# Set working directory
WORKDIR /app

# Install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy all files
COPY . .

# Start the app in development mode
CMD ["npm", "run", "dev"]
