# Use the official Nginx image from Docker Hub
FROM nginx:alpine

# Remove the default nginx website
RUN rm -rf /usr/share/nginx/html/*

# Copy the final dashboard file into the web server's public directory
COPY index_final.html /usr/share/nginx/html/index.html

# Expose port 80 to the Docker network
EXPOSE 80

# Start Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]
