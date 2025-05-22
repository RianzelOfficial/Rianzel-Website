FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy application code
COPY . .

# Build and serve
RUN npm run build

EXPOSE 3000
CMD ["npm", "run", "preview", "--", "--port", "3000"]
