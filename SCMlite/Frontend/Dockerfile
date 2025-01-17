FROM nginx:alpine

# Copy all files from the frontend directory to Nginx's default document root
COPY . /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
