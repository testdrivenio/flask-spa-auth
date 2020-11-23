# pull the official base image
FROM node:15.2.0-alpine

# set working directory
WORKDIR /usr/src/app

# add `/usr/src/app/node_modules/.bin` to $PATH
ENV PATH /usr/src/app/node_modules/.bin:$PATH
ENV HOST=0.0.0.0

# install and cache app dependencies
COPY package.json .
COPY package-lock.json .
RUN npm ci
RUN npm install svelte@3.0.0 -g --silent

# start app
CMD ["npm", "run", "dev"]
